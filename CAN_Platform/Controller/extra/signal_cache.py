import threading

class SignalCache:
    def __init__(self):
        self._lock = threading.Lock()
        self._data = {
            "rpm": 0,
            "temp": 0,
            "afr": 14.2,
            "tps": 0,
            "map": 0,
            "battery": 12.5,
            "dwell": 0,
            "timing": 0
        }

    def update(self, name, value):
        with self._lock:
            if name in self._data:
                self._data[name] = value

    def update_batch(self, data_dict):
        """Update multiple signals at once."""
        with self._lock:
            for key, value in data_dict.items():
                if key in self._data:
                    self._data[key] = value

    def get_all(self):
        with self._lock:
            return dict(self._data)

    def get_formatted_string(self):
        """Return signals as comma-separated string for BLE transmission."""
        with self._lock:
            # Format: rpm,temp,afr,tps,map,battery,dwell,timing
            return f"{int(self._data['rpm'])},{self._data['temp']:.1f},{self._data['afr']:.2f},{self._data['tps']:.1f},{self._data['map']:.1f},{self._data['battery']:.1f},{self._data['dwell']:.1f},{self._data['timing']:.1f}"

# Singleton instance
signal_cache = SignalCache()