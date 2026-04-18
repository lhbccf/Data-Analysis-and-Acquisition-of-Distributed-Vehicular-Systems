import sys
import serial
import threading
from queue import Queue
import time
from UI.ui_stuff import  temp_color, Gauge
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor
import pyqtgraph as pg
from UI.circulargauge import CircularGauge

class App(QtWidgets.QMainWindow):
    def __init__(self, data_queue):
        super().__init__()

        self.data_queue = data_queue

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
        while not self.data_queue.empty():
            d = self.data_queue.get()
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
