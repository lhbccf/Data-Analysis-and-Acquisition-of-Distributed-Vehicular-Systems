import re
from pathlib import Path


CONTROLLER_DIR = Path(__file__).resolve().parents[1]
DBC_PATH = CONTROLLER_DIR / "rusefi.dbc"


def parse_dbc_messages(path):
    messages = {}
    current_message = None

    for line in path.read_text().splitlines():
        message_match = re.match(r"BO_\s+(\d+)\s+(\w+):", line)
        if message_match:
            frame_id, name = message_match.groups()
            current_message = name
            messages[current_message] = {
                "frame_id": int(frame_id),
                "signals": set(),
            }
            continue

        signal_match = re.match(r"\s+SG_\s+(\w+)\s+:", line)
        if signal_match and current_message:
            messages[current_message]["signals"].add(signal_match.group(1))

    return messages


def test_rusefi_dbc_has_signals_used_by_the_producer():
    dbc_messages = parse_dbc_messages(DBC_PATH)

    expected_signals = {
        "BASE0": {"Fan", "FuelPumpAct"},
        "BASE1": {"RPM", "IgnitionTiming", "VehicleSpeed"},
        "BASE2": {"TPS1", "Wastegate"},
        "BASE3": {"MAP", "CoolantTemp", "IntakeTemp"},
        "BASE4": {"BattVolt"},
        "BASE5": {"InjPW"},
        "BASE7": {"Lam1"},
    }

    for message_name, signal_names in expected_signals.items():
        assert message_name in dbc_messages
        assert signal_names.issubset(dbc_messages[message_name]["signals"])


def test_base_messages_use_rusefi_standard_ids():
    dbc_messages = parse_dbc_messages(DBC_PATH)

    assert dbc_messages["BASE0"]["frame_id"] == 0x200
    assert dbc_messages["BASE1"]["frame_id"] == 0x201
    assert dbc_messages["BASE2"]["frame_id"] == 0x202
    assert dbc_messages["BASE3"]["frame_id"] == 0x203
    assert dbc_messages["BASE4"]["frame_id"] == 0x204
    assert dbc_messages["BASE5"]["frame_id"] == 0x205
    assert dbc_messages["BASE7"]["frame_id"] == 0x207
