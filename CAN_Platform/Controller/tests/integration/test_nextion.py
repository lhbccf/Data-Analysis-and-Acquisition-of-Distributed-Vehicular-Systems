import sys
import time
import json
import random
from pathlib import Path

import serial


CONTROLLER_DIR = Path(__file__).resolve().parents[2]
if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

from extra.signal_cache import DEFAULT_SIGNAL_DATA


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
        f"map={scenario['map']} "
        f"tps={scenario['tps']} "
        f"advance={scenario['advance']} "
        f"vss={scenario['vss']}"
    )


def send_cmd(ser, cmd):
    ser.write(cmd.encode())
    ser.write(b"\xff\xff\xff")
    ser.flush()


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def send_random_values_to_nextion(ser, values, redline, shift_point):
    rpm_percent = clamp(int((values["rpm"] / redline) * 100))
    clt_gauge = clamp(int(((values["clt"] - 60) / 60) * 100))
    afr_gauge = clamp(int(((values["afr"] - 10) / 10) * 100))
    shiftlight_color = 6400 if values["rpm"] > shift_point else 0

    commands = [
        f'rpm.txt="{int(values["rpm"])}"',
        f'afr.txt="AFR: {values["afr"]:.1f} AFR"',
        f'clt.txt="CLT: {int(values["clt"])} C"',
        f'adv.txt="ADV: {values["advance"]:.1f} deg"',
        f'map.txt="MAP: {values["map"]:.1f} kPa"',
        f'baro.txt="BARO: {values["baro"]:.1f} kPa"',
        f'tps.txt="TPS: {values["tps"]:.1f} %"',
        f'iat.txt="IAT: {int(values["iat"])} C"',
        f'ego.txt="EGO: {values["ego_correction"]:.0f} %"',
        f'pw.txt="PW: {values["pulse_width"]:.2f} ms"',
        f've.txt="VE: {int(values["ve"])} %"',
        f'dwell.txt="DWELL: {values["dwell"]:.1f} ms"',
        f'bat.txt="BAT: {values["battery_voltage"]:.1f} V"',
        f'boost.txt="BOOST: {values["boost_target"]:.1f} kPa"',
        f'duty.txt="DUTY: {values["boost_duty"]:.0f} %"',
        f'sync.txt="SYNC: {int(values["sync"])}"',
        f'engine.txt="ENGINE: {int(values["engine_status"])}"',
        f'fan.txt="FAN: {int(values["fan"])}"',
        f'fp.txt="FP: {int(values["fp"])}"',
        f'boostcut.txt="BOOSTCUT: {int(values["boost_cut"])}"',
        f'rpmgauge.val="{rpm_percent}"',
        f'cltgauge.val={clt_gauge}',
        f'afrgauge.val={afr_gauge}',
        f'vss.txt="VSS: {int(values["vss"])} km/h"',
        f'shiftlight.pco="{shiftlight_color}"',
    ]

    for command in commands:
        send_cmd(ser, command)


def generate_random_scenario(index):
    profiles = [
        ("Idle", 750, 1050, 13.8, 15.0, 70, 96, 5.0, 12.0, 0, 0),
        ("Cruise", 1800, 3300, 13.8, 14.9, 78, 98, 18.0, 34.0, 30, 120),
        ("Acceleration", 3500, 6800, 11.8, 13.3, 82, 104, 12.0, 28.0, 60, 180),
        ("Hot", 1800, 4200, 12.8, 14.4, 98, 112, 8.0, 22.0, 20, 100),
    ]

    name, rpm_min, rpm_max, afr_min, afr_max, clt_min, clt_max, adv_min, adv_max, vss_min, vss_max = random.choice(profiles)

    values = DEFAULT_SIGNAL_DATA.copy()
    values.update({
        "name": f"{name} #{index}",
        "rpm": random.randint(rpm_min, rpm_max),
        "afr": round(random.uniform(afr_min, afr_max), 1),
        "clt": random.randint(clt_min, clt_max),
        "iat": random.randint(25, 55),
        "map": round(random.uniform(30.0, 180.0), 1),
        "baro": round(random.uniform(99.0, 103.0), 1),
        "tps": round(random.uniform(0.0, 100.0), 1),
        "ego_correction": random.randint(90, 110),
        "pulse_width": round(random.uniform(1.0, 18.0), 2),
        "ve": random.randint(40, 120),
        "advance": round(random.uniform(adv_min, adv_max), 1),
        "dwell": round(random.uniform(2.0, 5.0), 1),
        "battery_voltage": round(random.uniform(12.0, 14.5), 1),
        "boost_target": round(random.uniform(80.0, 200.0), 1),
        "boost_duty": random.randint(0, 100),
        "vss": random.randint(vss_min, vss_max),
        "sync": 1,
        "engine_status": 1,
        "fan": random.choice([False, True]),
        "fp": True,
        "boost_cut": False,
        "timestamp": time.time(),
    })
    return values


def main():
    config = read_config_from_args()
    print(
        "Starting Nextion manual value test on "
        f"{config['nextion_port']} @ {config['nextion_baud']} baud"
    )
    print("Sending random values forever. Stop with Ctrl+C or systemctl stop.")
    print()

    ser = serial.Serial(
        port=config["nextion_port"],
        baudrate=config["nextion_baud"],
        timeout=1,
    )

    print("Serial opened. Waiting for display to be ready...")
    time.sleep(2.5)

    index = 1

    try:
        while True:
            values = generate_random_scenario(index)
            print_scenario(index, values)
            send_random_values_to_nextion(
                ser,
                values,
                config["redline"],
                config["shift_point"],
            )
            time.sleep(2)
            index += 1
    except KeyboardInterrupt:
        print()
        print("Nextion random value test stopped.")


if __name__ == "__main__":
    main()
