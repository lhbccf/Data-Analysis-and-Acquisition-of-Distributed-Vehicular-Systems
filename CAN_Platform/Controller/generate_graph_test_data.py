import argparse
import json
from pathlib import Path

from nextion.graph_renderer import build_graph_commands
from nextion.graph_test_data import DEFAULT_TEST_SIGNALS, generate_graph_rows


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic vehicle rows and matching Nextion graph commands."
    )
    parser.add_argument("--samples", type=int, default=180)
    parser.add_argument("--signals", default=",".join(DEFAULT_TEST_SIGNALS))
    parser.add_argument("--output", type=Path, default=Path("graph_test_output"))
    parser.add_argument("--redline", type=int, default=7500)
    args = parser.parse_args()

    signals = tuple(item.strip().lower() for item in args.signals.split(",") if item.strip())
    if not signals:
        parser.error("--signals must contain at least one signal")

    rows = generate_graph_rows(args.samples)
    commands = build_graph_commands(rows, signals, {"redline": args.redline})

    args.output.mkdir(parents=True, exist_ok=True)
    rows_path = args.output / "graph_rows.json"
    commands_path = args.output / "graph_commands.txt"
    rows_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    commands_path.write_text("\n".join(commands) + "\n", encoding="utf-8")

    print(f"Generated {len(rows)} rows in {rows_path}")
    print(f"Generated {len(commands)} commands in {commands_path}")


if __name__ == "__main__":
    main()
