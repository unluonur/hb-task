import os
from datetime import datetime
import time
from kafka import KafkaProducer
import json

if __name__ == '__main__':
    with open('data/product-views.json', 'r') as f:
        producer = KafkaProducer(bootstrap_servers=os.environ['BOOTSTRAP_SERVERS'])
        while True:
            line = f.readline()
            if not line or len(line) == 0:
                break
            obj = json.loads(line)
            obj['timestamp'] = datetime.now().isoformat()
            str_obj = str(obj)
            producer.send('product-view', str_obj.encode('utf-8'))
            print(str_obj)
            time.sleep(1)
