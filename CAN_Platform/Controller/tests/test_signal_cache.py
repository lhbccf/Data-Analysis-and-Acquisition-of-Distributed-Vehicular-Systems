import sys
from pathlib import Path


CONTROLLER_DIR = Path(__file__).resolve().parents[1]
if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

from extra.signal_cache import DEFAULT_SIGNAL_DATA, SignalCache


def test_cache_starts_with_default_signal_data():
    cache = SignalCache()

    data = cache.get_all()

    assert data["rpm"] == 0
    assert data["baro"] == 101.3
    assert data["battery_voltage"] == 12.5
    assert data["battery"] == 12.5
    assert data["decoded"] is False
    assert data["_version"] == 0
    assert set(DEFAULT_SIGNAL_DATA).issubset(data)


def test_single_update_syncs_new_names_to_legacy_aliases():
    cache = SignalCache()

    cache.update("clt", 91.2)
    cache.update("battery_voltage", 13.7)
    cache.update("advance", 24.5)
    cache.update("tps", 42.0)
    data = cache.get_all()

    assert data["temp"] == 91.2
    assert data["battery"] == 13.7
    assert data["timing"] == 24.5
    assert data["throttle"] == 42.0
    assert data["_version"] == 4


def test_batch_update_syncs_legacy_aliases_to_new_names():
    cache = SignalCache()

    cache.update_batch({
        "temp": 88.0,
        "battery": 14.1,
        "timing": 19.5,
        "throttle": 55.5,
    })
    data = cache.get_all()

    assert data["clt"] == 88.0
    assert data["battery_voltage"] == 14.1
    assert data["advance"] == 19.5
    assert data["tps"] == 55.5
    assert data["_version"] == 1


def test_get_all_returns_a_copy():
    cache = SignalCache()

    data = cache.get_all()
    data["rpm"] = 9999

    assert cache.get_all()["rpm"] == 0


def test_formatted_string_uses_legacy_mobile_order():
    cache = SignalCache()
    cache.update_batch({
        "rpm": 3120,
        "clt": 86.45,
        "afr": 14.678,
        "tps": 12.34,
        "map": 101.27,
        "battery_voltage": 13.76,
        "dwell": 3.24,
        "advance": 22.54,
    })

    assert cache.get_formatted_string() == (
        "3120,86.5,14.68,12.3,101.3,13.8,3.2,22.5"
    )
