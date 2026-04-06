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


class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Speeduino Dashboard")
        self.resize(600, 500)

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        # 🔥 RPM texto
        

        # 🔥 GAUGE RPM
        self.gauge = CircularGauge(
            min_value=0,
            max_value=8000,
            value=0,
            steps=8,
            start_angle=-180.0,
            end_angle=90.0,
            outer_circle_pen_color=QColor(137, 148, 153),
            outer_circle_brush_color=QColor(40, 40, 40),
            outer_circle_thickness=12,
            inner_ring_pen_color='darkred',
            inner_ring_brush_color='red',
            inner_circle_brush_color=QColor(20, 20, 20),
            number_font_size=8
        )

        layout.addWidget(self.gauge)
        self.rpm_label = QtWidgets.QLabel("0 RPM")
        self.rpm_label.setStyleSheet("font-size: 30px; color: white;")
        self.rpm_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.rpm_label)
        # 📊 TPS
        self.tps_bar = QtWidgets.QProgressBar()
        self.tps_bar.setMaximum(100)
        self.tps_bar.setFormat("TPS: %p%")
        layout.addWidget(self.tps_bar)

        # 📊 MAP
        self.map_bar = QtWidgets.QProgressBar()
        self.map_bar.setMaximum(200)
        self.map_bar.setFormat("MAP: %p kPa")
        layout.addWidget(self.map_bar)

        # 🌡️ temps
        temp_layout = QtWidgets.QHBoxLayout()

        self.iat_label = QtWidgets.QLabel("IAT")
        self.clt_label = QtWidgets.QLabel("CLT")

        temp_layout.addWidget(self.iat_label)
        temp_layout.addWidget(self.clt_label)

        layout.addLayout(temp_layout)

        # ⏱️ timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)

    def update_ui(self):
        while not data_queue.empty():
            d = data_queue.get()
            print(d)
            rpm = int(d["rpm"])

            # 🔥 atualizar gauge
            self.gauge.value = rpm
            self.gauge.update()

            # texto
            self.rpm_label.setText(f"{rpm} RPM")

            # barras
            self.tps_bar.setValue(int(d["tps"]))
            self.map_bar.setValue(int(d["map"]))

            # temps
            self.iat_label.setText(f"IAT: {d['iat']} °C")
            self.iat_label.setStyleSheet(
                f"color: {temp_color(d['iat'])}; font-size: 18px;"
            )

            self.clt_label.setText(f"CLT: {d['clt']} °C")
            self.clt_label.setStyleSheet(
                f"color: {temp_color(d['clt'])}; font-size: 18px;"
            )

# 🧵 thread serial
threading.Thread(target=serial_reader, daemon=True).start()

# ▶️ app
app = QtWidgets.QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec_())