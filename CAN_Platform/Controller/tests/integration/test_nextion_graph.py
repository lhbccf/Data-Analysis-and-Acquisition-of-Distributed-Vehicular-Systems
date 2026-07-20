import argparse
import json
import sys
import time
from pathlib import Path


CONTROLLER_DIR = Path(__file__).resolve().parents[2]
if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

from nextion.graph_renderer import SIGNAL_RANGES, build_graph_commands
from nextion.graph_test_data import generate_graph_rows
from nextion.writer import NEXTION_TERMINATOR


def load_config():
    config_path = CONTROLLER_DIR / "config.json"
    with config_path.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def parse_signals(value):
    if isinstance(value, (list, tuple)):
        value = ",".join(value)

    signals = tuple(signal.strip().lower() for signal in value.split(",") if signal.strip())
    if not signals:
        raise argparse.ArgumentTypeError("at least one signal is required")

    unknown = [signal for signal in signals if signal not in SIGNAL_RANGES]
    if unknown:
        raise argparse.ArgumentTypeError(
            "unsupported signal(s): " + ", ".join(unknown)
        )

    return signals


def main():
    config = load_config()
    parser = argparse.ArgumentParser(
        description="Generate synthetic vehicle data and draw it on a Nextion graph page."
    )
    parser.add_argument(
        "--port",
        default=config.get("nextion_port", "/dev/serial0"),
        help="Nextion serial device (default: value from config.json)",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=int(config.get("nextion_baud", 115200)),
        help="Nextion serial baud rate (default: value from config.json)",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=120,
        help="number of generated samples (default: 120)",
    )
    parser.add_argument(
        "--signals",
        type=parse_signals,
        default=parse_signals("rpm,afr,clt"),
        help="comma-separated signals (default: rpm,afr,clt)",
    )
    parser.add_argument(
        "--redline",
        type=int,
        default=int(config.get("redline", 7500)),
    )
    parser.add_argument(
        "--command-delay",
        type=float,
        default=0.01,
        help="delay between display commands (default: 0.01 seconds)",
    )
    args = parser.parse_args()

    if args.samples <= 0:
        parser.error("--samples must be greater than zero")
    if args.command_delay < 0:
        parser.error("--command-delay cannot be negative")

    try:
        import serial
    except ImportError as exc:
        raise SystemExit(
            "pyserial is not installed; run ./run_nextion_graph_test.sh"
        ) from exc

    rows = generate_graph_rows(args.samples)
    commands = build_graph_commands(
        rows,
        args.signals,
        {"redline": args.redline},
    )

    print("Nextion graph test parameters:")
    print(f"  port: {args.port}")
    print(f"  baud: {args.baud}")
    print(f"  samples: {args.samples}")
    print(f"  signals: {', '.join(args.signals)}")
    print(f"  redline: {args.redline} RPM")
    print(f"  command delay: {args.command_delay} s")
    print(f"  commands to send: {len(commands)}")
    print("Ensure the controller service is stopped so it does not use the same serial port.")

    with serial.Serial(args.port, args.baud, timeout=1) as display:
        time.sleep(2)
        bytes_written = 0

        for index, command in enumerate(commands, start=1):
            payload = command.encode("ascii") + NEXTION_TERMINATOR
            bytes_written += display.write(payload)
            display.flush()

            if index == 1:
                # Allow the Nextion time to change to the graph page.
                time.sleep(0.5)
            elif args.command_delay:
                time.sleep(args.command_delay)

            if index % 100 == 0:
                print(f"  sent {index}/{len(commands)} commands")

    print(
        f"Graph test complete: sent {len(commands)} commands "
        f"({bytes_written} bytes)."
    )


if __name__ == "__main__":
    main()
