FROM python:3.7

RUN apt update
RUN apt install default-jdk -y

WORKDIR .
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD spark-submit \
    --driver-class-path lib/postgresql-42.2.16.jar, \
    --jars lib/postgresql-42.2.16.jar \
    src/etl.py \
    --data-db-url $DATA_DB_URL \
    --data-db-user $DATA_DB_USER \
    --data-db-password $DATA_DB_PASSWORD \
    --api-db-url $API_DB_URL \
    --api-db-user $API_DB_USER \
    --api-db-password $API_DB_PASSWORD
