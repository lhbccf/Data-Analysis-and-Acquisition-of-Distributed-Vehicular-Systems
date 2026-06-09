from extra.signal_cache import signal_cache

_KNOWN_KEYS = set(signal_cache.get_all().keys())


def dispatch_signals(signal_list, frame=None):
    """
    Receives decoded signals from RequestController and updates SignalCache.
    Accepts both dict signals {'name': ..., 'value': ...} and Signal objects.
    Frame metadata is stored if a CANFrame is provided.
    """
    batch = {}

    for signal in signal_list:
        if isinstance(signal, dict):
            name  = signal.get("name", "").lower()
            value = signal.get("value")
        else:
            name  = getattr(signal, "signal_name", "").lower()
            value = getattr(signal, "value", None)

        if name in _KNOWN_KEYS:
            batch[name] = value

    if frame is not None:
        batch["can_id"]        = frame.can_id
        batch["can_dlc"]       = frame.dlc
        batch["can_data"]      = frame.data
        batch["can_timestamp"] = frame.timestamp

    if batch:
        signal_cache.update_batch(batch)
