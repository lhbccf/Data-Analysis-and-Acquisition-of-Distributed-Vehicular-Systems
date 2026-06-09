import sys
import time
import json
from pathlib import Path


CONTROLLER_DIR = Path(__file__).resolve().parents[2]
if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

from extra.signal_cache import signal_cache
from nextion.thread import start_nextion


SCENARIOS = [
    {
        "name": "Idle",
        "rpm": 850,
        "afr": 14.7,
        "clt": 72,
        "advance": 8.0,
        "vss": 0,
    },
    {
        "name": "Warm cruise",
        "rpm": 2450,
        "afr": 14.2,
        "clt": 86,
        "advance": 28.5,
        "vss": 58,
    },
    {
        "name": "Acceleration",
        "rpm": 5200,
        "afr": 12.8,
        "clt": 91,
        "advance": 22.0,
        "vss": 116,
    },
    {
        "name": "High temperature",
        "rpm": 3100,
        "afr": 13.4,
        "clt": 106,
        "advance": 16.5,
        "vss": 74,
    },
    {
        "name": "Back to idle",
        "rpm": 920,
        "afr": 14.6,
        "clt": 89,
        "advance": 9.5,
        "vss": 0,
    },
]


def read_config_from_args():
    config_path = CONTROLLER_DIR / "config.json"
    file_config = {}

    if config_path.exists():
        with config_path.open() as f:
            file_config = json.load(f)

    port = sys.argv[1] if len(sys.argv) > 1 else file_config.get("nextion_port", "/dev/serial0")
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else int(file_config.get("nextion_baud", 115200))

    return {
        "nextion_port": port,
        "nextion_baud": baud,
        "redline": int(file_config.get("redline", 7500)),
        "shift_point": int(file_config.get("shift_point", 6500)),
    }


def print_scenario(index, scenario):
    print(
        f"{index}. {scenario['name']}: "
        f"rpm={scenario['rpm']} "
        f"afr={scenario['afr']} "
        f"clt={scenario['clt']} "
        f"advance={scenario['advance']} "
        f"vss={scenario['vss']}"
    )


def main():
    config = read_config_from_args()
    print(
        "Starting Nextion manual value test on "
        f"{config['nextion_port']} @ {config['nextion_baud']} baud"
    )
    print("Watch the display fields: rpm, afr, clt, adv, vss")
    print()

    start_nextion(config)
    time.sleep(2.5)

    for index, scenario in enumerate(SCENARIOS, start=1):
        values = dict(scenario)
        values.pop("name")
        values["timestamp"] = time.time()

        print_scenario(index, scenario)
        signal_cache.update_batch(values)
        time.sleep(2)

    print()
    print("Manual Nextion value test finished.")


if __name__ == "__main__":
    main()
