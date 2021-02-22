from datetime import datetime, timedelta
from pyspark import SparkConf
from pyspark.sql import SparkSession
import pyspark.sql.functions as f
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Etl Arguments')
    parser.add_argument('--data-db-url')
    parser.add_argument('--data-db-user')
    parser.add_argument('--data-db-password')
    parser.add_argument('--api-db-url')
    parser.add_argument('--api-db-user')
    parser.add_argument('--api-db-password')

    args = parser.parse_args()

    data_db_url = args.data_db_url
    data_db_user = args.data_db_user
    data_db_password = args.data_db_password
    api_db_url = args.api_db_url
    api_db_user = args.api_db_user
    api_db_password = args.api_db_password

    conf = SparkConf().setAppName('etl app')

    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    products = spark.read\
        .format('jdbc')\
        .option('url', data_db_url)\
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", "data_db.products") \
        .option("user", data_db_user) \
        .option("password", data_db_password) \
        .load()

    orders = spark.read\
        .format('jdbc')\
        .option('url', data_db_url)\
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", "data_db.orders") \
        .option("user", data_db_user) \
        .option("password", data_db_password) \
        .load()\
        .filter(f.col('order_date') > datetime.now() - timedelta(days=30))

    order_items = spark.read\
        .format('jdbc')\
        .option('url', api_db_url)\
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", "data_db.order_items") \
        .option("user", api_db_user) \
        .option("password", api_db_password) \
        .load()

    # TODO : a temporary table might be used
    products\
        .join(order_items, on=products['product_id'] == order_items['product_id'], how='left')\
        .join(orders, on=order_items['order_id'] == orders['order_id'], how='left')\
        .groupBy(products['product_id'], products['category_id'])\
        .agg(f.countDistinct(orders['user_id']).alias('user_count'))\
        .write\
        .format('jdbc')\
        .mode('overwrite') \
        .option("url", api_db_url) \
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", "api_db.product_sales") \
        .option("user", api_db_user) \
        .option("password", api_db_password) \
        .option('truncate', True) \
        .save()
