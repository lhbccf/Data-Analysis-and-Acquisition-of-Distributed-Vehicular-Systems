import random
import sys
import time
from pathlib import Path


CONTROLLER_DIR = Path(__file__).resolve().parents[2]
if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

from extra.signal_cache import signal_cache
from nextion.thread import start_nextion


config = {
    "nextion_port": "/dev/serial0",
    "nextion_baud": 9600
}

start_nextion(config)

print("Sending random test data to Nextion...")


while True:

    fake_data = {
        "rpm": random.randint(800, 9000),
        "afr": round(random.uniform(10.0, 18.0), 1),
        "clt": random.randint(60, 110),
        "advance": round(random.uniform(0, 40), 1),
        "vss": random.randint(0, 220),
        "timestamp": time.time()
    }

    print(fake_data)

    signal_cache.update_batch(fake_data)

    time.sleep(0.2)
