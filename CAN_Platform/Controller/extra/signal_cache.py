import threading


DEFAULT_SIGNAL_DATA = {
    # ENGINE
    "rpm": 0,
    "sync": 0,
    "engine_status": 0,

    # LOADS
    "map": 0.0,
    "baro": 101.3,
    "tps": 0.0,

    # TEMPERATURES
    "iat": 0.0,
    "clt": 0.0,

    # FUELING
    "afr": 0.0,
    "ego_correction": 100,
    "pulse_width": 0.0,
    "ve": 0,

    # IGNITION
    "advance": 0.0,
    "dwell": 0.0,

    # ELECTRICAL
    "battery_voltage": 0.0,

    # BOOST
    "boost_target": 0.0,
    "boost_duty": 0.0,

    # VEHICLE
    "vss": 0,

    # FLAGS
    "fan": False,
    "fp": False,
    "boost_cut": False,

    # META
    "timestamp": 0,
    "type": "speeduino",
    "can_id": None,
    "can_dlc": None,
    "can_data": None,
    "can_message": None,
    "can_timestamp": None,
    "received_at": None,
    "decoded": False,
}


class SignalCache:
    def __init__(self):
        self._lock = threading.Lock()
        self._data = DEFAULT_SIGNAL_DATA.copy()

    def update(self, name, value):
        with self._lock:
            self._data[name] = value

    def update_batch(self, data_dict):
        """Update multiple signals at once."""
        with self._lock:
            self._data.update(data_dict)

    def get_all(self):
        with self._lock:
            return dict(self._data)

    def get_formatted_string(self):
        """Return signals as comma-separated string for BLE transmission."""
        with self._lock:
            # Format: rpm,temp,afr,tps,map,battery,dwell,timing
            return (
                f"{int(self._data['rpm'])},"
                f"{self._data['clt']:.1f},"
                f"{self._data['afr']:.2f},"
                f"{self._data['tps']:.1f},"
                f"{self._data['map']:.1f},"
                f"{self._data['battery_voltage']:.1f},"
                f"{self._data['dwell']:.1f},"
                f"{self._data['advance']:.1f}"
            )

# Singleton instance
signal_cache = SignalCache()
