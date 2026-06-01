import sys
import json
import time
from pathlib import Path
from transmitter.thread import start_bluetooth
from Producer.thread import start_producer
from nextion.thread import start_nextion
from repository.database.database_manager import database_setup
import logging
from extra.logging_setup import configure_logging

LOG_PATH = configure_logging()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


def resolve_relative_path(path):
    resolved_path = Path(path)

    if resolved_path.is_absolute():
        return str(resolved_path)

    return str(BASE_DIR / resolved_path)


def load_config(path=BASE_DIR / "config.json"):

    with open(path, "r") as f:
        config = json.load(f)

    for key in ["dbc"]:
        if key in config:
            config[key] = resolve_relative_path(config[key])

    return config


def main():

    config = load_config()
    logger.info("Controller starting. Log file: %s", LOG_PATH)

    database_setup()

    logger.info("Loaded config: %s", config)
    
    start_producer(config)

    if config.get("bluetooth_enabled", False):
        start_bluetooth(config)

    if config["mode"] == "pi_screen" :

      from PyQt5 import QtWidgets
      from UI.App import App
    
      app = QtWidgets.QApplication(sys.argv)

      window = App()
  
      window.show()
  
      sys.exit(app.exec_())
      while True:
        time.sleep(1)
        
    elif config["mode"] == "nextion" :
      start_nextion(config)
      while True:
        time.sleep(1)
      
    

if __name__ == "__main__":
    main()
