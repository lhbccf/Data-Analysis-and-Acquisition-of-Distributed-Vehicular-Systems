import serial
import threading
from queue import Queue
import time
import random


def parse_speeduino(data):
    def get16(i):
        return (data[i] << 8) | data[i + 1]

    rpm = get16(6)
    map_val = get16(18) / 10
    iat = get16(20) / 10
    clt = get16(22) / 10
    tps = get16(24) / 10

    return {
        "rpm": rpm,
        "map": map_val,
        "iat": iat,
        "clt": clt,
        "tps": tps
    }


def generate_fake_data():
    return {
        "rpm": random.randint(800, 7000),
        "map": round(random.uniform(20, 100), 1),
        "iat": round(random.uniform(10, 50), 1),
        "clt": round(random.uniform(70, 100), 1),
        "tps": round(random.uniform(0, 100), 1)
    }


def serial_reader(config, data_queue):
    mode = config.get("mode", "real")

    if mode == "real":
        ser = serial.Serial(
            config["com"],
            config["baud_rate"],
            timeout=1
        )

        command = config.get("command", "a").encode()

        while True:
            ser.write(command)
            data = ser.read(114)

            if len(data) == 114:
                parsed = parse_speeduino(data)
                data_queue.put(parsed)

    else:
        print("TEST MODE")
        while True:
            data_queue.put(generate_fake_data())
            time.sleep(0.5)


def start_producer(config, data_queue):
    thread = threading.Thread(
        target=serial_reader,
        args=(config, data_queue),
        daemon=True
    )
    thread.start()
    return thread