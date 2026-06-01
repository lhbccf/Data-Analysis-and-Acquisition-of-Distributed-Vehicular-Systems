import logging
import threading

logger = logging.getLogger(__name__)


def _resolve_adapter(config) -> str:
    """
    Return the BT adapter address to use.
    If 'bluetooth_adapter' is set in config, use it directly.
    Otherwise auto-detect the first adapter available on the device.
    """
    addr = config.get("bluetooth_adapter")
    if addr:
        return addr

    from bluezero import adapter as ble_adapter
    adapters = ble_adapter.list_adapters()
    if not adapters:
        raise RuntimeError("No Bluetooth adapter found on this device.")
    detected = adapters[0]
    logger.info("bluetooth_adapter not set — using detected adapter: %s", detected)
    return detected


def bluetooth_worker(config):
    try:
        from transmitter.bluetooth_transmitter import BLETlmServer
        adapter_address = _resolve_adapter(config)
        logger.info("BLE server starting (adapter=%s)", adapter_address)
        server = BLETlmServer(adapter_address=adapter_address)
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
