GRAPH_X = 35
GRAPH_Y = 45
GRAPH_WIDTH = 410
GRAPH_HEIGHT = 170
MAX_GRAPH_POINTS = GRAPH_WIDTH

WHITE = 65535
BLACK = 0
RED = 63488
GREEN = 2016
BLUE = 31
ORANGE = 64512
CYAN = 2047
MAGENTA = 63519
GRAY = 33808

SIGNAL_COLORS = [RED, BLUE, GREEN, ORANGE, CYAN, MAGENTA]

SIGNAL_RANGES = {
    "rpm": (0, 7500),
    "afr": (10, 20),
    "clt": (0, 120),
    "iat": (0, 80),
    "tps": (0, 100),
    "map": (0, 250),
    "baro": (80, 120),
    "advance": (-20, 60),
    "pulse_width": (0, 20),
    "battery_voltage": (0, 16),
    "boost_target": (0, 250),
    "boost_duty": (0, 100),
    "vss": (0, 250),
}


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def get_signal_range(signal, config=None):
    config = config or {}

    if signal == "rpm":
        return 0, int(config.get("redline", SIGNAL_RANGES["rpm"][1]))

    return SIGNAL_RANGES.get(signal, (0, 100))


def reduce_rows(rows, max_points=MAX_GRAPH_POINTS):
    if max_points <= 0:
        return []

    if len(rows) <= max_points:
        return rows

    if max_points == 1:
        return [rows[0]]

    # Spread samples over the complete session, including both endpoints.
    last_index = len(rows) - 1
    return [
        rows[round(index * last_index / (max_points - 1))]
        for index in range(max_points)
    ]


def value_to_y(value, minimum, maximum):
    if maximum == minimum:
        return GRAPH_Y + GRAPH_HEIGHT

    percent = (float(value) - minimum) / (maximum - minimum)
    percent = clamp(percent, 0, 1)

    return GRAPH_Y + GRAPH_HEIGHT - int(percent * GRAPH_HEIGHT)


def index_to_x(index, total_points):
    if total_points <= 1:
        return GRAPH_X

    percent = index / (total_points - 1)
    return GRAPH_X + int(percent * GRAPH_WIDTH)


def build_signal_lines(rows, signal, color, config=None):
    minimum, maximum = get_signal_range(signal, config)
    points = []

    for index, row in enumerate(rows):
        value = row.get(signal)
        if value is None:
            continue

        points.append((
            index_to_x(index, len(rows)),
            value_to_y(value, minimum, maximum),
        ))

    commands = []

    if len(points) == 1:
        x, y = points[0]
        return [f"cir {x},{y},2,{color}"]

    for index in range(1, len(points)):
        x1, y1 = points[index - 1]
        x2, y2 = points[index]
        commands.append(f"line {x1},{y1},{x2},{y2},{color}")

    return commands


def build_legend_commands(signals):
    commands = []

    for index, signal in enumerate(signals):
        color = SIGNAL_COLORS[index % len(SIGNAL_COLORS)]
        x = GRAPH_X + index * 70
        y = 20
        commands.append(f"fill {x},{y},10,10,{color}")
        commands.append(
            f'xstr {x + 14},{y - 3},55,18,0,{BLACK},{WHITE},0,1,1,"{signal}"'
        )

    return commands


def build_graph_commands(rows, signals, config=None):
    rows = reduce_rows(rows)
    commands = [
        "page graph",
        f"fill {GRAPH_X},{GRAPH_Y},{GRAPH_WIDTH},{GRAPH_HEIGHT},{WHITE}",
        f"line {GRAPH_X},{GRAPH_Y},{GRAPH_X},{GRAPH_Y + GRAPH_HEIGHT},{BLACK}",
        f"line {GRAPH_X},{GRAPH_Y + GRAPH_HEIGHT},"
        f"{GRAPH_X + GRAPH_WIDTH},{GRAPH_Y + GRAPH_HEIGHT},{BLACK}",
    ]

    commands.extend(build_legend_commands(signals))

    for index, signal in enumerate(signals):
        color = SIGNAL_COLORS[index % len(SIGNAL_COLORS)]
        commands.extend(build_signal_lines(rows, signal, color, config))

    if not rows:
        commands.append(
            f'xstr {GRAPH_X + 80},{GRAPH_Y + 70},220,25,0,{BLACK},'
            f'{WHITE},0,1,1,"No session data"'
        )

    return commands
