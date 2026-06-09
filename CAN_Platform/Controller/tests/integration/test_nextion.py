import sys
import time
import json
import random
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


def generate_random_scenario(index):
    profiles = [
        ("Idle", 750, 1050, 13.8, 15.0, 70, 96, 5.0, 12.0, 0, 0),
        ("Cruise", 1800, 3300, 13.8, 14.9, 78, 98, 18.0, 34.0, 30, 120),
        ("Acceleration", 3500, 6800, 11.8, 13.3, 82, 104, 12.0, 28.0, 60, 180),
        ("Hot", 1800, 4200, 12.8, 14.4, 98, 112, 8.0, 22.0, 20, 100),
    ]

    name, rpm_min, rpm_max, afr_min, afr_max, clt_min, clt_max, adv_min, adv_max, vss_min, vss_max = random.choice(profiles)

    return {
        "name": f"{name} #{index}",
        "rpm": random.randint(rpm_min, rpm_max),
        "afr": round(random.uniform(afr_min, afr_max), 1),
        "clt": random.randint(clt_min, clt_max),
        "advance": round(random.uniform(adv_min, adv_max), 1),
        "vss": random.randint(vss_min, vss_max),
    }


def main():
    config = read_config_from_args()
    print(
        "Starting Nextion manual value test on "
        f"{config['nextion_port']} @ {config['nextion_baud']} baud"
    )
    print("Sending random values forever. Stop with Ctrl+C or systemctl stop.")
    print()

    start_nextion(config)
    time.sleep(2.5)

    index = 1

    while True:
        scenario = generate_random_scenario(index)
        values = dict(scenario)
        values.pop("name")
        values["timestamp"] = time.time()

        print_scenario(index, scenario)
        signal_cache.update_batch(values)
        time.sleep(2)
        index += 1


if __name__ == "__main__":
    main()
