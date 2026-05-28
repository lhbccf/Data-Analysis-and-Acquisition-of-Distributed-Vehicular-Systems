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
    "afr": 14.2,
    "ego_correction": 100,
    "pulse_width": 0.0,
    "ve": 0,

    # IGNITION
    "advance": 0.0,
    "dwell": 0.0,

    # ELECTRICAL
    "battery_voltage": 12.5,

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
    "_version": 0,

    "temp": 0.0,
    "battery": 12.5,
    "timing": 0.0,
    "throttle": 0.0,
}


class SignalCache:
    def __init__(self):
        self._lock = threading.Lock()
        self._data = DEFAULT_SIGNAL_DATA.copy()

    def _sync_aliases(self, updated_keys):
        if "clt" in updated_keys:
            self._data["temp"] = self._data["clt"]
        elif "temp" in updated_keys:
            self._data["clt"] = self._data["temp"]

        if "battery_voltage" in updated_keys:
            self._data["battery"] = self._data["battery_voltage"]
        elif "battery" in updated_keys:
            self._data["battery_voltage"] = self._data["battery"]

        if "advance" in updated_keys:
            self._data["timing"] = self._data["advance"]
        elif "timing" in updated_keys:
            self._data["advance"] = self._data["timing"]

        if "tps" in updated_keys:
            self._data["throttle"] = self._data["tps"]
        elif "throttle" in updated_keys:
            self._data["tps"] = self._data["throttle"]

    def _mark_updated(self):
        self._data["_version"] += 1

    def update(self, name, value):
        with self._lock:
            self._data[name] = value
            self._sync_aliases({name})
            self._mark_updated()

    def update_batch(self, data_dict):
        with self._lock:
            self._data.update(data_dict)
            self._sync_aliases(set(data_dict.keys()))
            self._mark_updated()

    def get_all(self):
        with self._lock:
            return dict(self._data)

    def get_formatted_string(self):
        with self._lock:
            return (
                f"{int(self._data['rpm'])},"
                f"{self._data['temp']:.1f},"
                f"{self._data['afr']:.2f},"
                f"{self._data['tps']:.1f},"
                f"{self._data['map']:.1f},"
                f"{self._data['battery']:.1f},"
                f"{self._data['dwell']:.1f},"
                f"{self._data['timing']:.1f}"
            )

signal_cache = SignalCache()
