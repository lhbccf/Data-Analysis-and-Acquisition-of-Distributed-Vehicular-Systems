import sys
import json
from queue import Queue
from PyQt5 import QtWidgets
from transmitter.bluetooth_transmitter import BLEServer
from controller.RequestController import RequestController

from Producer.thread import start_producer
from UI.App import App


def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f) 

def main():
    config = load_config()
    data_queue = Queue()

    start_producer(config, data_queue)

    app = QtWidgets.QApplication(sys.argv)
    window = App(data_queue)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()