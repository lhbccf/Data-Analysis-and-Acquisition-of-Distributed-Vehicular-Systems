from domain import Signal
from services import Services

SIGNAL_DEFINITIONS = {
    0x0CFF: [
        {
            "name": "RPM",
            "start_byte": 0,
            "length": 2,
            "factor": 0.25,
            "offset": 0,
            "unit": "rpm"
        },
        {
            "name": "CoolantTemp",
            "start_byte": 2,
            "length": 1,
            "factor": 1,
            "offset": -40,
            "unit": "°C"
        }
    ]
}

def create_session(description: str):
    Services.create_session(description=description)

def create_can_frame(session_id: int, can_id: int, dlc: int, data: str):
    frame = Services.create_can_frame(session_id=session_id, can_id=can_id, dlc=dlc, data=data)
    signal_list = process_frame(frame_id=frame.id, can_id=can_id, data=data)
    for signal in signal_list:
        Services.create_signal(can_frame_id=frame.id, signal_name=signal["name"], signal_value=signal["value"], signal_unit=signal["unit"])

def create_signal(can_frame_id: int, signal_name: str, signal_value: str, signal_unit: str):
    Services.create_signal(can_frame_id=can_frame_id, signal_name=signal_name, signal_value=signal_value, signal_unit=signal_unit)

def end_session(session_id: int):
    Services.end_session(session_id=session_id)

def clear_session_frames(session_id: int):
    Services.clear_session_frames(session_id=session_id)

def close_database():
    Services.close_database()
    

def process_frame(frame_id: int, can_id: int, data: str):
    data_bytes = bytes.fromhex(data)

    if can_id not in SIGNAL_DEFINITIONS:
        return

    signal_list = []
    for signal in SIGNAL_DEFINITIONS[can_id]:
        value = decode_signal(data_bytes, signal)
        signal_list.append({"name": signal["name"], "value": value, "unit": signal["unit"]})
    return signal_list

def decode_signal(data_bytes, signal):
    start = signal["start_byte"]
    length = signal["length"]

    raw = int.from_bytes(data_bytes[start:start+length], 'big')

    value = raw * signal["factor"] + signal["offset"]
    return value