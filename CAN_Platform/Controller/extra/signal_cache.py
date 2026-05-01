import threading

class SignalCache:
    def __init__(self):
        self._lock = threading.Lock()
        self._data = {
            "rpm": 0,
            "temp": 0,
            "throttle": 0
        }

    def update(self, name, value):
        with self._lock:
            self._data[name] = value

    def get_all(self):
        with self._lock:
            return dict(self._data)

# Singleton instance
signal_cache = SignalCache()