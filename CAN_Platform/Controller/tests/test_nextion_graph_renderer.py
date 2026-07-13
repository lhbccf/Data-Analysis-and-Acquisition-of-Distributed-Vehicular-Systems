import sys
from pathlib import Path


CONTROLLER_DIR = Path(__file__).resolve().parents[1]
if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

from nextion.graph_renderer import (
    GRAPH_HEIGHT,
    GRAPH_WIDTH,
    GRAPH_X,
    GRAPH_Y,
    build_graph_commands,
    reduce_rows,
    value_to_y,
)


def test_reduce_rows_limits_number_of_points():
    rows = [{"rpm": index} for index in range(1000)]

    reduced = reduce_rows(rows, 100)

    assert len(reduced) == 100
    assert reduced[0]["rpm"] == 0
    assert reduced[-1]["rpm"] == 990


def test_value_to_y_converts_to_graph_coordinates():
    assert value_to_y(0, 0, 100) == GRAPH_Y + GRAPH_HEIGHT
    assert value_to_y(100, 0, 100) == GRAPH_Y
    assert value_to_y(50, 0, 100) == GRAPH_Y + int(GRAPH_HEIGHT / 2)


def test_build_graph_commands_draws_normalized_lines():
    rows = [
        {"rpm": 0, "afr": 10},
        {"rpm": 3750, "afr": 15},
        {"rpm": 7500, "afr": 20},
    ]

    commands = build_graph_commands(rows, ("rpm", "afr"), {"redline": 7500})

    assert commands[0] == "page graph"
    assert f"line {GRAPH_X},{GRAPH_Y + GRAPH_HEIGHT},240,130,63488" in commands
    assert f"line 240,130,{GRAPH_X + GRAPH_WIDTH},{GRAPH_Y},63488" in commands
    assert any('"rpm"' in command for command in commands)
    assert any('"afr"' in command for command in commands)
