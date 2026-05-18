import serial
import threading
from queue import Queue
import time
import random
import json
import struct
import cantools


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

    print(f"DBC loaded: {path}")

    return db



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
# UPDATE STATE FROM RUSEFI
# =========================================================

def update_rusefi_state(state, message_name, decoded):

    # =====================================================
    # BASE0
    # =====================================================

    if message_name == "BASE0":

        state["fan"] = bool(decoded.get("Fan", 0))
        state["fp"] = bool(decoded.get("FuelPumpAct", 0))

        state["sync"] = 1
        state["engine_status"] = 1

    # =====================================================
    # BASE1
    # =====================================================

    elif message_name == "BASE1":

        state["rpm"] = int(decoded.get("RPM", 0))

        state["advance"] = float(
            decoded.get("IgnitionTiming", 0)
        )

        state["vss"] = float(
            decoded.get("VehicleSpeed", 0)
        )

    # =====================================================
    # BASE2
    # =====================================================

    elif message_name == "BASE2":

        state["tps"] = float(
            decoded.get("TPS1", 0)
        )

        state["boost_duty"] = float(
            decoded.get("Wastegate", 0)
        )

    # =====================================================
    # BASE3
    # =====================================================

    elif message_name == "BASE3":

        state["map"] = float(
            decoded.get("MAP", 0)
        )

        state["clt"] = float(
            decoded.get("CoolantTemp", 0)
        )

        state["iat"] = float(
            decoded.get("IntakeTemp", 0)
        )

    # =====================================================
    # BASE4
    # =====================================================

    elif message_name == "BASE4":

        state["battery_voltage"] = float(
            decoded.get("BattVolt", 0)
        )

    # =====================================================
    # BASE5
    # =====================================================

    elif message_name == "BASE5":

        state["pulse_width"] = float(
            decoded.get("InjPW", 0)
        )

    # =====================================================
    # BASE7
    # =====================================================

    elif message_name == "BASE7":

        lam = float(decoded.get("Lam1", 0))

        if lam > 0:
            state["afr"] = lam * 14.7

    # =====================================================
    # UPDATE META
    # =====================================================

    state["timestamp"] = time.time()

    return state.copy()


# =========================================================
# GVRET FRAME PARSER
# =========================================================

def parse_gvret_frame(ser, config, dbc):

    global ecu_state

    start = ser.read(1)

    if not start:
        return None

    if start[0] != 0xF1:
        return None

    cmd = ser.read(1)

    if not cmd:
        return None

    cmd = cmd[0]

    if cmd == 0x00:

        header = ser.read(9)

        if len(header) < 9:
            return None

        timestamp = struct.unpack('<I', header[0:4])[0]

        canid_raw = struct.unpack('<I', header[4:8])[0]

        dlc_bus = header[8]

        dlc = dlc_bus & 0x0F

        data = ser.read(dlc)

        ser.read(1)

        canid = canid_raw & 0x1FFFFFFF

        try:

            message = dbc.get_message_by_frame_id(canid)

            # IGNORAR frames pequenas
            if dlc < message.length:
                return None

            decoded = message.decode(data)

            parsed = update_rusefi_state(
                ecu_state,
                message.name,
                decoded
            )

            parsed["can_id"] = canid
            parsed["can_message"] = message.name
            parsed["can_timestamp"] = timestamp

            return parsed

        except Exception as e:

            return None

    return None
# =========================================================
# CAN THREAD
# =========================================================


def can_reader(config, data_queue):

    dbc = load_dbc(config["dbc"])

    ser = serial.Serial(
        port=config["com"],
        baudrate=config["baud_rate"],
        timeout=1
    )

    # enable GVRET binary mode
    ser.write(bytes([0xE7]))

    print("GVRET binary mode enabled")

    while True:

        try:

            frame = parse_gvret_frame(
                ser,
                config,
                dbc
            )

            if frame:
                data_queue.put(frame)

        except Exception as e:

            print(f"CAN ERROR: {e}")

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


def speeduino_reader(config, data_queue):

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

                data_queue.put(parsed)

        except Exception as e:

            print(f"SPEEDUINO ERROR: {e}")

            time.sleep(1)




def start_speeduino(config, data_queue):

    thread = threading.Thread(
        target=speeduino_reader,
        args=(config, data_queue),
        daemon=True
    )

    thread.start()

    return thread


def start_can(config, data_queue):

    thread = threading.Thread(
        target=can_reader,
        args=(config, data_queue),
        daemon=True
    )

    thread.start()

    return thread



def load_config(path="../config.json"):

    with open(path, "r") as f:
        return json.load(f)

def start_producer(config, data_queue):

    mode = config.get("type")

    if mode == "speeduino_arduino":

        thread = threading.Thread(
            target=speeduino_reader,
            args=(config, data_queue),
            daemon=True
        )

        thread.start()

        print("Speeduino thread started")

        return thread

    elif mode == "rusefi_can":

        thread = threading.Thread(
            target=can_reader,
            args=(config, data_queue),
            daemon=True
        )

        thread.start()

        print("CAN/GVRET thread started")

        return thread

    else:

        raise ValueError(
            f"Unknown mode: {mode}"
        )
