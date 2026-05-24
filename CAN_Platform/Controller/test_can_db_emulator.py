import importlib.util
import sqlite3
import struct
import sys
import tempfile
import types
import unittest
from contextlib import closing
from pathlib import Path


for optional_module in ("serial", "cantools"):
    if importlib.util.find_spec(optional_module) is None:
        sys.modules[optional_module] = types.ModuleType(optional_module)

from Producer import thread as producer_thread
from repository import CANFrameRepo, SessionRepo, SignalRepo, StateRepo
from repository.database import database_manager
from services import Services


class FakeSerial:
    def __init__(self, payload):
        self.payload = bytearray(payload)

    def read(self, size):
        data = self.payload[:size]
        del self.payload[:size]
        return bytes(data)


class FakeMessage:
    def __init__(self, name, length, decoder):
        self.name = name
        self.length = length
        self.decoder = decoder

    def decode(self, data):
        return self.decoder(data)


class FakeDBC:
    def __init__(self, messages):
        self.messages = messages

    def get_message_by_frame_id(self, can_id):
        return self.messages[can_id]


def build_gvret_frame(can_id, data, timestamp):
    header = struct.pack("<I", timestamp)
    header += struct.pack("<I", can_id)
    header += bytes([len(data) & 0x0F])

    return bytes([0xF1, 0x00]) + header + data + bytes([0x00])


def make_fake_dbc():
    return FakeDBC({
        0x100: FakeMessage(
            "BASE0",
            2,
            lambda data: {
                "Fan": data[0],
                "FuelPumpAct": data[1],
            },
        ),
        0x101: FakeMessage(
            "BASE1",
            6,
            lambda data: {
                "RPM": struct.unpack("<H", data[0:2])[0],
                "IgnitionTiming": struct.unpack("<h", data[2:4])[0] / 10,
                "VehicleSpeed": struct.unpack("<H", data[4:6])[0] / 10,
            },
        ),
        0x103: FakeMessage(
            "BASE3",
            6,
            lambda data: {
                "MAP": struct.unpack("<H", data[0:2])[0] / 10,
                "CoolantTemp": struct.unpack("<h", data[2:4])[0] / 10,
                "IntakeTemp": struct.unpack("<h", data[4:6])[0] / 10,
            },
        ),
        0x104: FakeMessage(
            "BASE4",
            2,
            lambda data: {
                "BattVolt": struct.unpack("<H", data[0:2])[0] / 10,
            },
        ),
        0x107: FakeMessage(
            "BASE7",
            2,
            lambda data: {
                "Lam1": struct.unpack("<H", data[0:2])[0] / 1000,
            },
        ),
    })


class CANDatabaseEmulatorTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "ecu_data_test.db")
        self.original_paths = {
            database_manager: database_manager.DB_PATH,
            SessionRepo: SessionRepo.DB_PATH,
            CANFrameRepo: CANFrameRepo.DB_PATH,
            SignalRepo: SignalRepo.DB_PATH,
            StateRepo: StateRepo.DB_PATH,
        }

        for module in self.original_paths:
            module.DB_PATH = self.db_path

        database_manager.database_setup()
        self.original_ecu_state = producer_thread.ecu_state.copy()

    def tearDown(self):
        producer_thread.ecu_state.clear()
        producer_thread.ecu_state.update(self.original_ecu_state)

        for module, db_path in self.original_paths.items():
            module.DB_PATH = db_path

        self.temp_dir.cleanup()

    def test_emulated_can_frames_are_saved_to_database(self):
        mapping = producer_thread.load_state_mapping(
            Path(__file__).with_name("rusefi_state_mapping.json")
        )
        dbc = make_fake_dbc()
        session = Services.create_session("emulated CAN DB test")

        frames = [
            build_gvret_frame(0x100, bytes([1, 1]), 1000),
            build_gvret_frame(
                0x101,
                struct.pack("<HhH", 3500, 225, 802),
                1001,
            ),
            build_gvret_frame(
                0x103,
                struct.pack("<Hhh", 1234, 865, 312),
                1002,
            ),
            build_gvret_frame(0x104, struct.pack("<H", 138), 1003),
            build_gvret_frame(0x107, struct.pack("<H", 1000), 1004),
            build_gvret_frame(0x999, bytes.fromhex("01 02 03 04"), 1005),
        ]

        ser = FakeSerial(b"".join(frames))

        for _ in frames:
            frame = producer_thread.parse_gvret_frame(
                ser,
                {},
                dbc,
                mapping,
            )

            Services.create_can_frame(
                session_id=session.id,
                can_id=frame["can_id"],
                dlc=frame["can_dlc"],
                data=frame["can_data"],
                timestamp=frame["received_at"],
            )

            if frame.get("decoded"):
                Services.create_vehicle_state(frame)

        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            can_frame_count = cursor.execute(
                "SELECT COUNT(*) AS total FROM can_frames"
            ).fetchone()["total"]
            state_count = cursor.execute(
                "SELECT COUNT(*) AS total FROM vehicle_state"
            ).fetchone()["total"]
            latest_state = cursor.execute(
                "SELECT * FROM vehicle_state ORDER BY id DESC LIMIT 1"
            ).fetchone()

        self.assertEqual(can_frame_count, 6)
        self.assertEqual(state_count, 5)
        self.assertEqual(latest_state["rpm"], 3500)
        self.assertEqual(latest_state["sync"], 1)
        self.assertEqual(latest_state["engine_status"], 1)
        self.assertEqual(latest_state["fan"], 1)
        self.assertEqual(latest_state["fp"], 1)
        self.assertAlmostEqual(latest_state["advance"], 22.5)
        self.assertAlmostEqual(latest_state["vss"], 80.2)
        self.assertAlmostEqual(latest_state["map"], 123.4)
        self.assertAlmostEqual(latest_state["clt"], 86.5)
        self.assertAlmostEqual(latest_state["iat"], 31.2)
        self.assertAlmostEqual(latest_state["battery_voltage"], 13.8)
        self.assertAlmostEqual(latest_state["afr"], 14.7)

        print(
            f"Saved {can_frame_count} CAN frames and "
            f"{state_count} vehicle_state snapshots in {self.db_path}"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
