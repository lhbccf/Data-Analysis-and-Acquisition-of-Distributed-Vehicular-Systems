import sys
import serial
import threading
from queue import Queue
import time
from ui_stuff import  temp_color, Gauge
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor
import pyqtgraph as pg
from circulargauge import CircularGauge

data_queue = Queue()

def parse_speeduino(data):
    def get16(i):
        return (data[i] << 8) | data[i+1]

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

def serial_reader():
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

    while True:
        ser.write(b'a')

        data = ser.read(114)

        if len(data) == 114:
            parsed = parse_speeduino(data)
            data_queue.put(parsed)
            #print(list(data))

