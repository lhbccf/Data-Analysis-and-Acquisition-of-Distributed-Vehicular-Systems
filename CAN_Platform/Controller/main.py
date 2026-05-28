import sys
import json
from queue import Queue
from PyQt5 import QtWidgets
from transmitter.bluetooth_transmitter import BLEServer
from controller.RequestController import RequestController

import time
from Producer.thread import start_producer
from nextion.thread import start_nextion
from UI.App import App
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s',
)

logger = logging.getLogger(__name__)

def load_config(path="config.json"):

    with open(path, "r") as f:
        return json.load(f) 

def main():

    config = load_config()

    data_queue = Queue()

    print(config)
    
    start_producer(config, data_queue)
    
    if config["mode"] == "pi_screen" :
    
      app = QtWidgets.QApplication(sys.argv)

      window = App(data_queue)
  
      window.show()
  
      sys.exit(app.exec_())
      while True:
        time.sleep(1)
        
    elif config["mode"] == "nextion" :
      start_nextion(config, data_queue)
      while True:
        time.sleep(1)
      
    

if __name__ == "__main__":
    main()