import argparse
import json
import sys
from pathlib import Path


CONTROLLER_DIR = Path(__file__).resolve().parents[2]
if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

from nextion.graph_renderer import SIGNAL_RANGES, build_graph_commands
from nextion.graph_test_data import DEFAULT_TEST_SIGNALS, generate_graph_rows
from nextion.writer import nextion_writer


def load_config():
    config_path = CONTROLLER_DIR / "config.json"
    with config_path.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def parse_signals(value):
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
    parser.add_argument("--samples", type=int, default=180)
    parser.add_argument(
        "--signals",
        type=parse_signals,
        default=parse_signals(",".join(DEFAULT_TEST_SIGNALS)),
        help="comma-separated signals to draw",
    )
    parser.add_argument(
        "--redline",
        type=int,
        default=int(config.get("redline", 7500)),
    )
    args = parser.parse_args()

    if args.samples <= 0:
        parser.error("--samples must be greater than zero")

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

    print(
        f"Opening Nextion on {args.port} at {args.baud} baud; "
        f"drawing {len(rows)} samples for {', '.join(args.signals)}."
    )

    with serial.Serial(args.port, args.baud, timeout=1) as display:
        bytes_written, commands_sent = nextion_writer.write_batch(display, commands)

    print(
        f"Graph test complete: sent {commands_sent} commands "
        f"({bytes_written} bytes)."
    )


if __name__ == "__main__":
    main()
