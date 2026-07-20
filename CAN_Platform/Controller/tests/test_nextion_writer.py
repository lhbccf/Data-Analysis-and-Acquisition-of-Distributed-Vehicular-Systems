import logging
import sys
import threading
from pathlib import Path


CONTROLLER_DIR = Path(__file__).resolve().parents[1]
if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

from nextion.writer import NEXTION_TERMINATOR, nextion_writer


class FakeSerial:
    def __init__(self):
        self.writes = []
        self.flushes = 0

    def write(self, data):
        self.writes.append(data)
        return len(data)

    def flush(self):
        self.flushes += 1


class BrokenSerial:
    def write(self, data):
        raise OSError("serial unavailable")


def test_writer_adds_terminators_and_flushes_once_per_batch():
    serial_port = FakeSerial()

    byte_count, command_count = nextion_writer.write_batch(
        serial_port,
        ("page graph", "line 1,2,3,4,5"),
    )

    assert command_count == 2
    assert byte_count == len(b"page graphline 1,2,3,4,5") + 6
    assert serial_port.writes == [
        b"page graph",
        NEXTION_TERMINATOR,
        b"line 1,2,3,4,5",
        NEXTION_TERMINATOR,
    ]
    assert serial_port.flushes == 1


def test_concurrent_batches_are_not_interleaved():
    serial_port = FakeSerial()
    gate = threading.Barrier(3)

    def submit(commands):
        gate.wait()
        nextion_writer.write_batch(serial_port, commands)

    first = threading.Thread(target=submit, args=(("A1", "A2", "A3"),))
    second = threading.Thread(target=submit, args=(("B1", "B2", "B3"),))
    first.start()
    second.start()
    gate.wait()
    first.join()
    second.join()

    commands = [item.decode() for item in serial_port.writes if item != NEXTION_TERMINATOR]
    assert commands in [
        ["A1", "A2", "A3", "B1", "B2", "B3"],
        ["B1", "B2", "B3", "A1", "A2", "A3"],
    ]


def test_writer_propagates_serial_errors_to_caller():
    logging.disable(logging.CRITICAL)
    try:
        try:
            nextion_writer.write(BrokenSerial(), "page graph")
        except OSError as exc:
            assert str(exc) == "serial unavailable"
        else:
            raise AssertionError("Expected serial error")
    finally:
        logging.disable(logging.NOTSET)
