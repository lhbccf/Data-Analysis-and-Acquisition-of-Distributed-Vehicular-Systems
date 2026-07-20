import sys
from pathlib import Path


CONTROLLER_DIR = Path(__file__).resolve().parents[1]
if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

from nextion.graph_renderer import build_graph_commands
from nextion.graph_test_data import generate_graph_rows


def test_generated_graph_data_is_deterministic_and_renderable():
    rows = generate_graph_rows(samples=500)

    assert len(rows) == 500
    assert rows[0]["rpm"] == 900
    assert rows[-1]["rpm"] == 900
    assert max(row["rpm"] for row in rows) >= 6999
    assert all(10 <= row["afr"] <= 20 for row in rows)

    commands = build_graph_commands(rows, ("rpm", "afr", "clt"), {"redline": 7500})

    assert commands[0] == "page graph"
    assert sum(command.startswith("line ") for command in commands) > 1000


def test_generated_graph_data_supports_empty_sessions():
    assert generate_graph_rows(samples=0) == []
