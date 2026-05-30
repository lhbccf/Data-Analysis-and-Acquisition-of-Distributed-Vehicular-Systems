import logging
import threading
import time

from nextion.graph_requests import handle_nextion_request
from nextion.protocol import parse_nextion_message


logger = logging.getLogger(__name__)


def nextion_reader_worker(ser, config, stop_event=None, on_request=None):
    stop_event = stop_event or threading.Event()
    on_request = on_request or handle_nextion_request
    max_message_size = int(config.get("nextion_rx_max_message_size", 256))
    buffer = bytearray()

    logger.info("Nextion RX thread started")

    while not stop_event.is_set():
        try:
            chunk = ser.read(1)

            if not chunk:
                time.sleep(0.01)
                continue

            byte = chunk[0]

            if byte == 0xFF:
                continue

            buffer.append(byte)

            if byte != ord("|"):
                if len(buffer) > max_message_size:
                    logger.warning("Dropping oversized Nextion RX message")
                    buffer.clear()
                continue

            raw_message = bytes(buffer)
            buffer.clear()

            request = parse_nextion_message(raw_message)
            if request is None:
                logger.debug("Ignoring Nextion RX message: %r", raw_message)
                continue

            on_request(ser, request, config)

        except Exception as exc:
            logger.exception("Nextion RX error: %s", exc)
            buffer.clear()
            time.sleep(0.5)


def start_nextion_reader(ser, config, on_request=None):
    thread = threading.Thread(
        target=nextion_reader_worker,
        args=(ser, config),
        kwargs={"on_request": on_request},
        daemon=True,
        name="NextionRxThread",
    )
    thread.start()
    return thread
