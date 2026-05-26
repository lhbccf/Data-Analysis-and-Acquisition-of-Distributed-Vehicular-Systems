import serial
import threading
import time
import random
import json
import struct
import cantools
import logging
from services import Services
from extra.signal_cache import signal_cache

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)

gvret_parser_stats = {
    "empty_reads": 0,
    "bad_start_bytes": 0,
    "empty_commands": 0,
    "unknown_commands": 0,
    "short_headers": 0,
    "short_payloads": 0,
    "decoded_errors": 0,
}


# =========================================================
# HELPERS
# =========================================================

def get16(data, i):
    return (data[i] << 8) | data[i + 1]


def get_signed16(data, i):
    value = get16(data, i)

    if value >= 32768:
        value -= 65536

    return value


def parse_speeduino(data):

    parsed = {

        # ENGINE
        "rpm": get16(data, 6),
        "sync": data[4],
        "engine_status": data[5],

        # LOADS
        "map": get16(data, 18) / 10,
        "baro": get16(data, 26) / 10,
        "tps": get16(data, 24) / 10,

        # TEMPERATURES
        "iat": get_signed16(data, 20) / 10,
        "clt": get_signed16(data, 22) / 10,

        # FUELING
        "afr": get16(data, 10) / 10,
        "ego_correction": data[11],
        "pulse_width": get16(data, 14) / 1000,
        "ve": data[17],

        # IGNITION
        "advance": get_signed16(data, 30) / 10,
        "dwell": get16(data, 32) / 10,

        # ELECTRICAL
        "battery_voltage": get16(data, 28) / 10,

        # BOOST
        "boost_target": get16(data, 34) / 10,
        "boost_duty": data[36],

        # VEHICLE
        "vss": get16(data, 38),

        # FLAGS
        "fan": bool(data[40] & 0x01),
        "fp": bool(data[40] & 0x02),
        "boost_cut": bool(data[40] & 0x04),

        "timestamp": time.time()
    }

    return parsed



def load_dbc(path):

    db = cantools.database.load_file(path)

    logger.info(f"DBC loaded: {path}")

    return db


def load_state_mapping(path):

    with open(path, "r") as f:
        mapping = json.load(f)

    logger.info(f"State mapping loaded: {path}")

    return mapping



def rusefi_to_speeduino(decoded):

    # decoded = dict com sinais da DBC

    return {

        # ENGINE
        "rpm": int(decoded.get("RPMValue", 0)),
        "sync": 1,
        "engine_status": 1,

        # LOADS
        "map": float(decoded.get("MAPValue", 0)),
        "baro": float(decoded.get("BaroPressure", 101.3)),
        "tps": float(decoded.get("TPSValue", 0)),

        # TEMPERATURES
        "iat": float(decoded.get("IAT", 0)),
        "clt": float(decoded.get("CLT", 0)),

        # FUELING
        "afr": float(decoded.get("Lambda", 0)) * 14.7,
        "ego_correction": 100,
        "pulse_width": float(decoded.get("InjectionPW", 0)),
        "ve": 0,

        # IGNITION
        "advance": float(decoded.get("IgnitionAdvance", 0)),
        "dwell": float(decoded.get("Dwell", 0)),

        # ELECTRICAL
        "battery_voltage": float(decoded.get("BatteryVoltage", 0)),

        # BOOST
        "boost_target": float(decoded.get("BoostTarget", 0)),
        "boost_duty": float(decoded.get("BoostDuty", 0)),

        # VEHICLE
        "vss": float(decoded.get("VehicleSpeed", 0)),

        # FLAGS
        "fan": False,
        "fp": True,
        "boost_cut": False,

        "timestamp": time.time(),

        "type": "speeduino"
    }


# =========================================================
# GVRET FRAME PARSER
# =========================================================
# =========================================================
# GLOBAL ECU STATE
# =========================================================

ecu_state = {

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
    "type": "speeduino"
}


# =========================================================
# UPDATE STATE FROM DBC MAPPING
# =========================================================

def convert_mapped_value(value, value_type):

    if value_type == "bool":
        return bool(value)

    if value_type == "int":
        return int(value)

    if value_type == "float":
        return float(value)

    return value


def should_ignore_mapped_value(value, rule):

    if rule.get("ignore_if_zero") and float(value) == 0:
        return True

    if "ignore_if_lte" in rule and float(value) <= rule["ignore_if_lte"]:
        return True

    if "ignore_if_gte" in rule and float(value) >= rule["ignore_if_gte"]:
        return True

    return False


def apply_signal_rule(decoded, rule):

    source = rule.get("source")

    if source not in decoded:
        if "default" not in rule:
            return None

        value = rule["default"]

    else:
        value = decoded[source]

    if should_ignore_mapped_value(value, rule):
        return None

    if rule.get("type") == "bool":
        return convert_mapped_value(value, "bool")

    value = float(value) * rule.get("scale", 1) + rule.get("offset", 0)

    return convert_mapped_value(
        value,
        rule.get("type")
    )


def update_rusefi_state(state, message_name, decoded, state_mapping):

    message_rules = state_mapping.get("messages", {}).get(message_name)

    if not message_rules:
        return None

    for target, value in message_rules.get("constants", {}).items():
        state[target] = value

    for target, rule in message_rules.get("signals", {}).items():
        value = apply_signal_rule(decoded, rule)

        if value is not None:
            state[target] = value

    state["timestamp"] = time.time()

    return state.copy()


# =========================================================
# GVRET FRAME PARSER
# =========================================================

def parse_gvret_frame(ser, config, dbc, state_mapping):

    global ecu_state
    global gvret_parser_stats

    start = ser.read(1)

    if not start:
        gvret_parser_stats["empty_reads"] += 1
        return None

    if start[0] != 0xF1:
        gvret_parser_stats["bad_start_bytes"] += 1
        return None

    cmd = ser.read(1)

    if not cmd:
        gvret_parser_stats["empty_commands"] += 1
        return None

    cmd = cmd[0]

    if cmd == 0x00:

        header = ser.read(9)

        if len(header) < 9:
            gvret_parser_stats["short_headers"] += 1
            return None

        timestamp = struct.unpack('<I', header[0:4])[0]

        canid_raw = struct.unpack('<I', header[4:8])[0]

        dlc_bus = header[8]

        dlc = dlc_bus & 0x0F

        data = ser.read(dlc)

        ser.read(1)

        if len(data) < dlc:
            gvret_parser_stats["short_payloads"] += 1

        canid = canid_raw & 0x1FFFFFFF

        raw_frame = {
            "can_id": canid,
            "can_dlc": dlc,
            "can_data": data.hex(),
            "can_timestamp": timestamp,
            "received_at": time.time(),
            "decoded": False
        }

        try:

            message = dbc.get_message_by_frame_id(canid)

            # IGNORAR frames pequenas
            if dlc < message.length:
                return raw_frame

            decoded = message.decode(data)

            parsed = update_rusefi_state(
                ecu_state,
                message.name,
                decoded,
                state_mapping
            )

            if not parsed:
                return raw_frame

            parsed["can_id"] = canid
            parsed["can_dlc"] = dlc
            parsed["can_data"] = data.hex()
            parsed["can_message"] = message.name
            parsed["can_timestamp"] = timestamp
            parsed["received_at"] = raw_frame["received_at"]
            parsed["decoded"] = True

            return parsed

        except Exception as e:

            gvret_parser_stats["decoded_errors"] += 1
            return raw_frame

    gvret_parser_stats["unknown_commands"] += 1
    return None
# =========================================================
# CAN THREAD
# =========================================================


def can_reader(config):

    dbc = load_dbc(config["dbc"])
    state_mapping = load_state_mapping(
        config.get("state_mapping", "./rusefi_state_mapping.json")
    )

    session = Services.create_session(
        config.get("session_description", "CAN acquisition")
    )

    last_state_save = 0
    state_save_interval = float(
        config.get("state_save_interval", 1.0)
    )

    ser = serial.Serial(
        port=config["com"],
        baudrate=config["baud_rate"],
        timeout=1
    )

    # enable GVRET binary mode
    ser.write(bytes([0xE7]))

    logger.info("GVRET binary mode enabled")
    logger.info(f"CAN DB session started: {session.id}")

    can_log_interval = float(config.get("can_log_interval", 5.0))
    log_can_activity = bool(config.get("log_can_activity", True))
    last_can_log = time.time()
    frames_seen = 0
    decoded_seen = 0
    undecoded_seen = 0
    latest_frame = None
    last_parser_stats = gvret_parser_stats.copy()

    while True:

        try:

            frame = parse_gvret_frame(
                ser,
                config,
                dbc,
                state_mapping
            )

            now = time.time()

            if frame:
                frames_seen += 1
                latest_frame = frame

                Services.create_can_frame(
                    session_id=session.id,
                    can_id=frame["can_id"],
                    dlc=frame["can_dlc"],
                    data=frame["can_data"],
                    timestamp=frame.get("received_at")
                )

                if not frame.get("decoded"):
                    undecoded_seen += 1
                else:
                    decoded_seen += 1

                    if now - last_state_save >= state_save_interval:
                        Services.create_vehicle_state(frame)
                        last_state_save = now

                    signal_cache.update_batch(frame)

            if log_can_activity and now - last_can_log >= can_log_interval:
                parser_delta = {
                    key: gvret_parser_stats[key] - last_parser_stats.get(key, 0)
                    for key in gvret_parser_stats
                }

                if latest_frame:
                    logger.info(
                        "CAN activity: frames=%s decoded=%s undecoded=%s "
                        "latest_id=0x%X latest_msg=%s latest_dlc=%s "
                        "parser=%s",
                        frames_seen,
                        decoded_seen,
                        undecoded_seen,
                        latest_frame["can_id"],
                        latest_frame.get("can_message", "unknown"),
                        latest_frame.get("can_dlc"),
                        parser_delta,
                    )
                else:
                    logger.warning(
                        "CAN reader alive, but no GVRET CAN frames received "
                        "in the last %.1fs. parser=%s",
                        can_log_interval,
                        parser_delta,
                    )

                last_can_log = now
                last_parser_stats = gvret_parser_stats.copy()
                frames_seen = 0
                decoded_seen = 0
                undecoded_seen = 0
                latest_frame = None

        except Exception as e:

            logger.info(f"CAN ERROR: {e}")

            time.sleep(1)


def generate_fake_data():

    return {

        "rpm": random.randint(800, 8000),
        "sync": 1,
        "engine_status": 1,

        "map": round(random.uniform(30, 180), 1),
        "baro": 101.3,
        "tps": round(random.uniform(0, 100), 1),

        "iat": round(random.uniform(15, 50), 1),
        "clt": round(random.uniform(70, 100), 1),

        "afr": round(random.uniform(11.5, 15.5), 2),
        "ego_correction": random.randint(90, 110),
        "pulse_width": round(random.uniform(1.0, 18.0), 2),
        "ve": random.randint(40, 120),

        "advance": round(random.uniform(5, 40), 1),
        "dwell": round(random.uniform(2, 5), 1),

        "battery_voltage": round(random.uniform(12.0, 14.5), 1),

        "boost_target": round(random.uniform(100, 200), 1),
        "boost_duty": random.randint(0, 100),

        "vss": random.randint(0, 220),

        "fan": random.choice([True, False]),
        "fp": True,
        "boost_cut": False,

        "timestamp": time.time()
    }


def speeduino_reader(config):

    ser = serial.Serial(
        port=config["port"],
        baudrate=config["baudrate"],
        timeout=1
    )

    command = config.get("command", "A").encode()

    while True:

        try:

            ser.write(command)

            data = ser.read(114)

            if len(data) == 114:

                parsed = parse_speeduino(data)

                parsed["type"] = "speeduino"

                signal_cache.update_batch(parsed)

        except Exception as e:

            logger.info(f"SPEEDUINO ERROR: {e}")

            time.sleep(1)




def start_speeduino(config, data_queue=None):

    thread = threading.Thread(
        target=speeduino_reader,
        args=(config,),
        daemon=True
    )

    thread.start()

    return thread


def start_can(config, data_queue=None):

    thread = threading.Thread(
        target=can_reader,
        args=(config,),
        daemon=True
    )

    thread.start()

    return thread



def load_config(path="../config.json"):

    with open(path, "r") as f:
        return json.load(f)

def start_producer(config, data_queue=None):

    mode = config.get("type")

    if mode == "speeduino_arduino":

        thread = threading.Thread(
            target=speeduino_reader,
            args=(config,),
            daemon=True
        )

        thread.start()

        logger.info("Speeduino thread started")

        return thread

    elif mode == "rusefi_can":

        thread = threading.Thread(
            target=can_reader,
            args=(config,),
            daemon=True
        )

        thread.start()

        logger.info("CAN/GVRET thread started")

        return thread

    else:

        raise ValueError(
            f"Unknown mode: {mode}"
        )
