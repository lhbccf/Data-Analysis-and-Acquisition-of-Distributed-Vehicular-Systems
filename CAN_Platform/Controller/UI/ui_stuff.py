from PyQt5 import QtWidgets, QtCore, QtGui

def temp_color(value):
    if value > 100:
        return "red"
    elif value > 85:
        return "orange"
    else:
        return "lightgreen"

class Gauge(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.value = 0

    def setValue(self, val):
        self.value = val
        self.update()

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QColor, QPen
        from PyQt5.QtCore import QRectF

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(10, 10, 200, 200)

        # fundo
        painter.setPen(QPen(QColor("gray"), 10))
        painter.drawArc(rect, 0, 360 * 16)

        # valor (RPM)
        painter.setPen(QPen(QColor("red"), 10))
        angle = int((self.value / 8000) * 360)
        painter.drawArc(rect, 0, -angle * 16)

