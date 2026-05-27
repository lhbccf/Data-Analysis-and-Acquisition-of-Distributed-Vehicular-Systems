import importlib.util
import sqlite3
import struct
import sys
import tempfile
import types
from contextlib import closing, contextmanager
from pathlib import Path


CONTROLLER_DIR = Path(__file__).resolve().parents[1]
if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

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
        0x200: FakeMessage(
            "BASE0",
            8,
            lambda data: {
                "FuelPumpAct": (data[4] >> 2) & 0x01,
                "Fan": (data[4] >> 6) & 0x01,
            },
        ),
        0x201: FakeMessage(
            "BASE1",
            8,
            lambda data: {
                "RPM": struct.unpack("<H", data[0:2])[0],
                "IgnitionTiming": struct.unpack("<h", data[2:4])[0] * 0.02,
                "VehicleSpeed": data[6],
            },
        ),
        0x202: FakeMessage(
            "BASE2",
            8,
            lambda data: {
                "TPS1": struct.unpack("<h", data[2:4])[0] * 0.01,
                "Wastegate": struct.unpack("<h", data[6:8])[0] * 0.01,
            },
        ),
        0x203: FakeMessage(
            "BASE3",
            8,
            lambda data: {
                "MAP": struct.unpack("<H", data[0:2])[0] * 0.03333333,
                "CoolantTemp": data[2] - 40,
                "IntakeTemp": data[3] - 40,
            },
        ),
        0x204: FakeMessage(
            "BASE4",
            8,
            lambda data: {
                "BattVolt": struct.unpack("<H", data[6:8])[0] * 0.001,
            },
        ),
        0x205: FakeMessage(
            "BASE5",
            8,
            lambda data: {
                "InjPW": struct.unpack("<H", data[4:6])[0] * 0.003333333,
            },
        ),
        0x207: FakeMessage(
            "BASE7",
            8,
            lambda data: {
                "Lam1": struct.unpack("<H", data[0:2])[0] * 0.0001,
            },
        ),
    })


@contextmanager
def isolated_database():
    temp_dir = tempfile.TemporaryDirectory()
    db_path = str(Path(temp_dir.name) / "ecu_data_test.db")
    original_paths = {
        database_manager: database_manager.DB_PATH,
        SessionRepo: SessionRepo.DB_PATH,
        CANFrameRepo: CANFrameRepo.DB_PATH,
        SignalRepo: SignalRepo.DB_PATH,
        StateRepo: StateRepo.DB_PATH,
    }
    original_ecu_state = producer_thread.ecu_state.copy()

    try:
        for module in original_paths:
            module.DB_PATH = db_path

        database_manager.database_setup()
        yield db_path
    finally:
        producer_thread.ecu_state.clear()
        producer_thread.ecu_state.update(original_ecu_state)

        for module, path in original_paths.items():
            module.DB_PATH = path

        temp_dir.cleanup()


def fetch_database_summary(db_path):
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        can_frame_count = cursor.execute(
            "SELECT COUNT(*) AS total FROM can_frames"
        ).fetchone()["total"]
        state_count = cursor.execute(
            "SELECT COUNT(*) AS total FROM vehicle_state"
        ).fetchone()["total"]
        raw_unknown_frame = cursor.execute(
            "SELECT * FROM can_frames WHERE can_id = ?",
            (0x999,),
        ).fetchone()
        latest_state = cursor.execute(
            "SELECT * FROM vehicle_state ORDER BY id DESC LIMIT 1"
        ).fetchone()

    return can_frame_count, state_count, raw_unknown_frame, latest_state


def test_emulated_can_frames_are_saved_to_database():
    with isolated_database() as db_path:
        mapping = producer_thread.load_state_mapping(
            CONTROLLER_DIR / "rusefi_state_mapping.json"
        )
        dbc = make_fake_dbc()
        session = Services.create_session("emulated CAN DB test")

        frames = [
            build_gvret_frame(0x200, bytes([0, 0, 0, 0, 0b01000100, 0, 0, 0]), 1000),
            build_gvret_frame(
                0x201,
                struct.pack("<HhBBBx", 3500, 1125, 0, 0, 80),
                1001,
            ),
            build_gvret_frame(
                0x202,
                struct.pack("<HhHh", 0, 4225, 0, 5550),
                1002,
            ),
            build_gvret_frame(
                0x203,
                struct.pack("<HBBBBBB", 3702, 126, 71, 0, 0, 0, 0),
                1003,
            ),
            build_gvret_frame(
                0x204,
                bytes([0, 0, 0, 0, 0, 0]) + struct.pack("<H", 13800),
                1004,
            ),
            build_gvret_frame(
                0x205,
                bytes([0, 0, 0, 0]) + struct.pack("<H", 1260) + bytes([0, 0]),
                1005,
            ),
            build_gvret_frame(0x207, struct.pack("<H", 10000) + bytes(6), 1006),
            build_gvret_frame(0x999, bytes.fromhex("01 02 03 04"), 1005),
        ]

        ser = FakeSerial(b"".join(frames))
        parsed_frames = []

        for _ in frames:
            frame = producer_thread.parse_gvret_frame(ser, {}, dbc, mapping)
            parsed_frames.append(frame)

            Services.create_can_frame(
                session_id=session.id,
                can_id=frame["can_id"],
                dlc=frame["can_dlc"],
                data=frame["can_data"],
                timestamp=frame["received_at"],
            )

            if frame.get("decoded"):
                Services.create_vehicle_state(frame)

        can_frame_count, state_count, raw_unknown_frame, latest_state = (
            fetch_database_summary(db_path)
        )

    assert len(parsed_frames) == 8
    assert parsed_frames[-1]["decoded"] is False
    assert parsed_frames[-1]["can_id"] == 0x999
    assert can_frame_count == 8
    assert state_count == 7
    assert raw_unknown_frame["data"] == "01020304"
    assert latest_state["rpm"] == 3500
    assert latest_state["sync"] == 1
    assert latest_state["engine_status"] == 1
    assert latest_state["fan"] == 1
    assert latest_state["fp"] == 1
    assert latest_state["advance"] == 22.5
    assert latest_state["vss"] == 80
    assert latest_state["tps"] == 42.25
    assert latest_state["boost_duty"] == 55.5
    assert round(latest_state["map"], 2) == 123.40
    assert latest_state["clt"] == 86
    assert latest_state["iat"] == 31
    assert latest_state["battery_voltage"] == 13.8
    assert round(latest_state["pulse_width"], 2) == 4.20
    assert latest_state["afr"] == 14.7


def test_short_gvret_payload_is_not_decoded():
    mapping = producer_thread.load_state_mapping(
        CONTROLLER_DIR / "rusefi_state_mapping.json"
    )
    ser = FakeSerial(build_gvret_frame(0x201, bytes([0xAA, 0xBB]), 2000))

    frame = producer_thread.parse_gvret_frame(ser, {}, make_fake_dbc(), mapping)

    assert frame["can_id"] == 0x201
    assert frame["can_dlc"] == 2
    assert frame["can_data"] == "aabb"
    assert frame["decoded"] is False
