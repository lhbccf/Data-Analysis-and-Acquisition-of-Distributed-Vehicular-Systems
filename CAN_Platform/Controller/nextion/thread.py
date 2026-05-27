import serial
import threading
import time
import logging
from extra.signal_cache import signal_cache
from extra.logging_setup import configure_logging

LOG_PATH = configure_logging()
logger = logging.getLogger(__name__)


def send_cmd(ser, cmd):

    payload = cmd.encode()
    terminator = b'\xff\xff\xff'
    written = ser.write(payload)
    written_terminator = ser.write(terminator)
    if hasattr(ser, "flush"):
        ser.flush()
    return (written or len(payload)) + (written_terminator or len(terminator))


def update_nextion(ser, data):

    try:

        bytes_written = send_cmd(
            ser,
            f'rpm.txt="{int(data["rpm"])}"'
        )

        bytes_written += send_cmd(
            ser,
            f'afr.txt="{data["afr"]:.1f}"'
        )

        bytes_written += send_cmd(
            ser,
            f'clt.txt="{int(data["clt"])}C"'
        )

        bytes_written += send_cmd(
            ser,
            f'adv.txt="{data["advance"]:.1f}"'
        )

        bytes_written += send_cmd(
            ser,
            f'vss.txt="{int(data["vss"])}"'
        )

        logger.info(
            "sent to nextion: version=%s decoded=%s bytes=%s "
            "rpm=%s afr=%.1f clt=%s advance=%.1f vss=%s",
            data.get("_version"),
            data.get("decoded"),
            bytes_written,
            int(data["rpm"]),
            float(data["afr"]),
            int(data["clt"]),
            float(data["advance"]),
            int(data["vss"]),
        )

        return True

    except Exception as e:

        logger.exception(f"NEXTION UPDATE ERROR: {e}")
        return False


def nextion_worker(config):

    try:

        ser = serial.Serial(
            port=config["nextion_port"],
            baudrate=config.get("nextion_baud", 115200),
            timeout=1
        )

        time.sleep(2)

        logger.info(
            "Nextion connected on %s @ %s is_open=%s",
            ser.port,
            ser.baudrate,
            ser.is_open,
        )

    except Exception as e:

        logger.exception(f"SERIAL INIT ERROR: {e}")
        return

    last_version = None

    while True:

        try:

            data = signal_cache.get_all()
            version = data.get("_version")

            if version != last_version:

                if update_nextion(ser, data):
                    last_version = version

            time.sleep(0.1)

        except Exception as e:

            logger.exception(f"NEXTION ERROR: {e}")

            time.sleep(1)


def start_nextion(config):

    thread = threading.Thread(
        target=nextion_worker,
        args=(config,),
        daemon=True,
        name="NextionThread"
    )

    thread.start()

    logger.info("Nextion thread started")

    return thread
