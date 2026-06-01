import logging
import threading

logger = logging.getLogger(__name__)


def bluetooth_worker(config):
    try:
        from transmitter.bluetooth_transmitter import BLETlmServer
        adapter = config.get("bluetooth_adapter", "")
        logger.info("BLE server starting (adapter=%s)", adapter)
        server = BLETlmServer(adapter_address=adapter)
        server.start()
    except Exception as exc:
        logger.exception("BLE server error: %s", exc)


def start_bluetooth(config):
    thread = threading.Thread(
        target=bluetooth_worker,
        args=(config,),
        daemon=True,
        name="BLEThread"
    )
    thread.start()
    logger.info("BLE thread started")
    return thread
