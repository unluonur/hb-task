from pyspark import SparkConf
from pyspark.sql import SparkSession, Window
from pyspark.sql.types import StructType, StringType, TimestampType
import pyspark.sql.functions as f
import psycopg2
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Etl Arguments')
    parser.add_argument('--db-host')
    parser.add_argument('--db-port')
    parser.add_argument('--db-name')
    parser.add_argument('--db-user')
    parser.add_argument('--db-password')

    args = parser.parse_args()

    db_host = args.db_host
    db_port = args.db_port
    db_name = args.db_name
    db_user = args.db_user
    db_password = args.db_password

    conf = SparkConf().setAppName('my app')

    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    event_schema = StructType() \
        .add('event', StringType(), True) \
        .add('messageid', StringType(), True) \
        .add('userid', StringType(), True) \
        .add('properties', StructType().add('productid', StringType()), True) \
        .add('context', StructType().add('source', StringType()), True)\
        .add('timestamp', TimestampType())

    product_views = spark.readStream.format('kafka')\
        .option('kafka.bootstrap.servers', 'kafka:9092') \
        .option('subscribe', 'product-view') \
        .option("startingOffsets", "latest") \
        .load()\
        .selectExpr("CAST(value AS STRING) as value")\
        .select(f.from_json('value', event_schema).alias('value'))\
        .select(f.col('value')['userid'].alias('user_id'),
                f.col('value')['properties']['productid'].alias('product_id'),
                f.col('value')['timestamp'].alias('visit_date'))

    def upsert_df(partition):
        con = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        try:
            cur = con.cursor()
            try:
                sql = '''
    INSERT INTO api_db.product_visits ( user_id, product_id, visit_date) values (%s, %s, %s)
    ON CONFLICT (user_id, product_id)
    DO UPDATE SET visit_date = %s;
                '''
                for row in partition:
                    print('row')
                    print(str(row))
                    cur.execute(sql, (row['user_id'], row['product_id'], row['visit_date'], row['visit_date']))
                con.commit()
            finally:
                cur.close()
        except Exception as er:
            print(str(er))
            con.rollback()
            raise
        finally:
            con.close()


    def batch_fn(df, batch_id):
        df.withColumn('rnk', f.row_number().over(Window.partitionBy('user_id').orderBy(f.col('visit_date').desc()))) \
            .filter(f.col('rnk') <= 10) \
            .select('user_id', 'product_id', 'visit_date') \
            .foreachPartition(upsert_df)

    query = product_views \
        .groupBy('user_id', 'product_id').agg(f.max('visit_date').alias('visit_date'))\
        .writeStream\
        .outputMode("update") \
        .foreachBatch(batch_fn) \
        .trigger(processingTime='60 seconds')\
        .start()

    query.awaitTermination()
