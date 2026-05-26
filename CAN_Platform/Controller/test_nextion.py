import random
import time
from queue import Queue

from nextion.thread import start_nextion


config = {
    "nextion_port": "/dev/serial0",
    "nextion_baud": 9600
}

data_queue = Queue()

start_nextion(config, data_queue)

print("Sending random test data to Nextion...")


while True:

    fake_data = {
        "rpm": random.randint(800, 9000),
        "afr": round(random.uniform(10.0, 18.0), 1),
        "clt": random.randint(60, 110),
        "advance": round(random.uniform(0, 40), 1),
        "vss": random.randint(0, 220)
    }

    print(fake_data)

    data_queue.put(fake_data)

    time.sleep(0.2)