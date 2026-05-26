from extra.signal_cache import signal_cache

def dispatch_signals(signal_list):
    """
    Receives decoded signals from RequestController
    and updates shared memory.
    """
    for signal in signal_list:
        name = signal["name"].lower()

        # Normalize names (important!)
        if name == "rpm":
            signal_cache.update("rpm", int(signal["value"]))
        elif name in ["temperature", "temp"]:
            signal_cache.update("clt", int(signal["value"]))
        elif name == "throttle":
            signal_cache.update("tps", int(signal["value"]))
