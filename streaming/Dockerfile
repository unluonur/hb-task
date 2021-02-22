FROM python:3.7

RUN apt update
RUN apt install default-jdk -y

# required to install psycopg2
RUN apt install libpq-dev

WORKDIR .
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD spark-submit \
    --driver-class-path lib/postgresql-42.2.16.jar \
    --jars lib/postgresql-42.2.16.jar \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1 \
    src/app.py \
    --db-host $DB_HOST \
    --db-port $DB_PORT \
    --db-name $DB_NAME \
    --db-user $DB_USER \
    --db-password $DB_PASSWORD

