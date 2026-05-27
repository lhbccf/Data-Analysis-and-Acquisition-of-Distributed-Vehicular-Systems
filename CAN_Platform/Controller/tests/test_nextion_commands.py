import importlib.util
import logging
import sys
import types
from pathlib import Path


CONTROLLER_DIR = Path(__file__).resolve().parents[1]
if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

if "serial" not in sys.modules and importlib.util.find_spec("serial") is None:
    sys.modules["serial"] = types.ModuleType("serial")

from nextion.thread import update_nextion


class FakeSerial:
    def __init__(self):
        self.writes = []

    def write(self, data):
        self.writes.append(data)


class BrokenSerial:
    def write(self, data):
        raise OSError("serial write failed")


def test_update_nextion_sends_expected_hardcoded_fields():
    ser = FakeSerial()

    ok = update_nextion(ser, {
        "rpm": 3120,
        "afr": 14.68,
        "clt": 86,
        "advance": 22.54,
        "vss": 58,
    })

    assert ok is True
    assert ser.writes == [
        b'rpm.txt="3120"',
        b"\xff\xff\xff",
        b'afr.txt="14.7"',
        b"\xff\xff\xff",
        b'clt.txt="86C"',
        b"\xff\xff\xff",
        b'adv.txt="22.5"',
        b"\xff\xff\xff",
        b'vss.txt="58"',
        b"\xff\xff\xff",
    ]


def test_update_nextion_reports_serial_write_failure():
    logging.disable(logging.CRITICAL)
    try:
        ok = update_nextion(BrokenSerial(), {
            "rpm": 3120,
            "afr": 14.68,
            "clt": 86,
            "advance": 22.54,
            "vss": 58,
        })
    finally:
        logging.disable(logging.NOTSET)

    assert ok is False
