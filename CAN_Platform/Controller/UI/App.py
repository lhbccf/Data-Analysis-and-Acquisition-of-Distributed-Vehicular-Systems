import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor, QFont
from UI.ui_stuff import temp_color
from UI.circulargauge import CircularGauge
from extra.signal_cache import signal_cache


class InfoCard(QtWidgets.QFrame):

    def __init__(self, title, value="---", unit=""):

        super().__init__()

        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 12px;
                border: 1px solid #333;
            }
        """)

        layout = QtWidgets.QVBoxLayout()

        self.title = QtWidgets.QLabel(title)
        self.title.setStyleSheet("""
            color: #888;
            font-size: 14px;
        """)

        self.value = QtWidgets.QLabel(value)

        self.value.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
        """)

        self.value.setAlignment(QtCore.Qt.AlignCenter)

        self.unit = QtWidgets.QLabel(unit)

        self.unit.setStyleSheet("""
            color: #666;
            font-size: 12px;
        """)

        self.unit.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.addWidget(self.unit)

        self.setLayout(layout)

    def set_value(self, value, color="white"):

        self.value.setText(str(value))

        self.value.setStyleSheet(f"""
            color: {color};
            font-size: 28px;
            font-weight: bold;
        """)


class App(QtWidgets.QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("ECU Dashboard")

        self.resize(1200, 700)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #111;
            }

            QLabel {
                color: white;
            }

            QProgressBar {
                border: 1px solid #333;
                border-radius: 6px;
                background: #1e1e1e;
                text-align: center;
                height: 26px;
                color: white;
                font-size: 14px;
            }

            QProgressBar::chunk {
                background-color: #00aa55;
                border-radius: 5px;
            }
        """)

        # =====================================================
        # CENTRAL
        # =====================================================

        central = QtWidgets.QWidget()

        self.setCentralWidget(central)

        root = QtWidgets.QHBoxLayout()

        central.setLayout(root)

        # =====================================================
        # LEFT SIDE
        # =====================================================

        left = QtWidgets.QVBoxLayout()

        root.addLayout(left, 2)

        # =====================================================
        # RPM GAUGE
        # =====================================================

        self.gauge = CircularGauge(
            min_value=0,
            max_value=9000,
            value=0,
            steps=9,
            start_angle=-210.0,
            end_angle=30.0,
            outer_circle_pen_color=QColor(80, 80, 80),
            outer_circle_brush_color=QColor(30, 30, 30),
            outer_circle_thickness=18,
            inner_ring_pen_color=QColor(200, 30, 30),
            inner_ring_brush_color=QColor(255, 40, 40),
            inner_circle_brush_color=QColor(10, 10, 10),
            number_font_size=10
        )

        left.addWidget(self.gauge)

        self.rpm_label = QtWidgets.QLabel("0 RPM")

        self.rpm_label.setAlignment(QtCore.Qt.AlignCenter)

        self.rpm_label.setStyleSheet("""
            font-size: 52px;
            font-weight: bold;
            color: white;
        """)

        left.addWidget(self.rpm_label)

        # =====================================================
        # BARS
        # =====================================================

        self.tps_bar = QtWidgets.QProgressBar()
        self.tps_bar.setMaximum(100)

        self.map_bar = QtWidgets.QProgressBar()
        self.map_bar.setMaximum(250)

        left.addWidget(self.tps_bar)
        left.addWidget(self.map_bar)

        # =====================================================
        # STATUS
        # =====================================================

        status_layout = QtWidgets.QHBoxLayout()

        self.sync_status = QtWidgets.QLabel("SYNC")
        self.fp_status = QtWidgets.QLabel("FP")
        self.fan_status = QtWidgets.QLabel("FAN")

        for lbl in [
            self.sync_status,
            self.fp_status,
            self.fan_status
        ]:

            lbl.setAlignment(QtCore.Qt.AlignCenter)

            lbl.setStyleSheet("""
                background-color: #222;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            """)

            status_layout.addWidget(lbl)

        left.addLayout(status_layout)

        # =====================================================
        # RIGHT SIDE
        # =====================================================

        right = QtWidgets.QGridLayout()

        root.addLayout(right, 3)

        self.cards = {}

        card_data = [

            ("TPS", "%"),
            ("MAP", "kPa"),
            ("AFR", ""),
            ("CLT", "°C"),
            ("IAT", "°C"),
            ("ADV", "°"),
            ("BAT", "V"),
            ("BOOST", "kPa"),
            ("DUTY", "%"),
            ("VSS", "km/h"),
            ("PW", "ms"),
            ("DWELL", "ms")
        ]

        row = 0
        col = 0

        for name, unit in card_data:

            card = InfoCard(name, "---", unit)

            right.addWidget(card, row, col)

            self.cards[name] = card

            col += 1

            if col > 2:
                col = 0
                row += 1

        # =====================================================
        # TIMER
        # =====================================================

        self.timer = QtCore.QTimer()

        self.timer.timeout.connect(self.update_ui)

        self.timer.start(30)

    # =========================================================
    # UPDATE UI
    # =========================================================

    def update_ui(self):

        d = signal_cache.get_all()

        rpm = int(d.get("rpm", 0))

        # =================================================
        # RPM
        # =================================================

        self.gauge.value = rpm
        self.gauge.update()

        rpm_color = "#ff3333" if rpm > 7000 else "white"

        self.rpm_label.setText(f"{rpm}")

        self.rpm_label.setStyleSheet(f"""
            font-size: 52px;
            font-weight: bold;
            color: {rpm_color};
        """)

        # =================================================
        # BARS
        # =================================================

        tps = float(d.get("tps", 0))
        mapv = float(d.get("map", 0))

        self.tps_bar.setValue(int(tps))
        self.tps_bar.setFormat(f"TPS {tps:.1f}%")

        self.map_bar.setValue(int(mapv))
        self.map_bar.setFormat(f"MAP {mapv:.1f} kPa")

        # =================================================
        # STATUS
        # =================================================

        self.set_status(
            self.sync_status,
            "SYNC",
            d.get("sync", 0)
        )

        self.set_status(
            self.fp_status,
            "FP",
            d.get("fp", False)
        )

        self.set_status(
            self.fan_status,
            "FAN",
            d.get("fan", False)
        )

        # =================================================
        # CARDS
        # =================================================

        self.cards["TPS"].set_value(
            f"{tps:.1f}"
        )

        self.cards["MAP"].set_value(
            f"{mapv:.1f}"
        )

        self.cards["AFR"].set_value(
            f"{d.get('afr', 0):.2f}",
            "#00ffaa"
        )

        self.cards["CLT"].set_value(
            f"{d.get('clt', 0):.1f}",
            temp_color(d.get("clt", 0))
        )

        self.cards["IAT"].set_value(
            f"{d.get('iat', 0):.1f}",
            temp_color(d.get("iat", 0))
        )

        self.cards["ADV"].set_value(
            f"{d.get('advance', 0):.1f}"
        )

        self.cards["BAT"].set_value(
            f"{d.get('battery_voltage', 0):.1f}",
            "#ffff66"
        )

        self.cards["BOOST"].set_value(
            f"{d.get('boost_target', 0):.1f}"
        )

        self.cards["DUTY"].set_value(
            f"{d.get('boost_duty', 0):.0f}"
        )

        self.cards["VSS"].set_value(
            f"{d.get('vss', 0):.0f}"
        )

        self.cards["PW"].set_value(
            f"{d.get('pulse_width', 0):.2f}"
        )

        self.cards["DWELL"].set_value(
            f"{d.get('dwell', 0):.1f}"
        )

    # =========================================================
    # STATUS HELPER
    # =========================================================

    def set_status(self, widget, text, active):

        color = "#00cc66" if active else "#444"

        widget.setText(text)

        widget.setStyleSheet(f"""
            background-color: {color};
            border-radius: 10px;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
            color: white;
        """)
