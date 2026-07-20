import math


DEFAULT_TEST_SIGNALS = ("rpm", "afr", "clt", "tps", "vss")


def generate_graph_rows(samples=180, interval_seconds=0.25, start_timestamp=0.0):
    """Build deterministic, plausible vehicle data for graph testing."""
    if samples < 0:
        raise ValueError("samples must be zero or greater")
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be greater than zero")

    rows = []
    denominator = max(samples - 1, 1)

    for index in range(samples):
        progress = index / denominator
        run = math.sin(progress * math.pi)
        throttle = max(0.0, math.sin(progress * math.pi * 3))
        rpm = 900 + 6100 * run

        rows.append({
            "timestamp": round(start_timestamp + index * interval_seconds, 3),
            "rpm": round(rpm),
            "afr": round(14.7 - 2.4 * throttle + 0.15 * math.sin(index / 4), 2),
            "clt": round(72 + 26 * progress, 1),
            "iat": round(24 + 12 * progress + 2 * throttle, 1),
            "tps": round(4 + 88 * throttle, 1),
            "map": round(35 + 165 * throttle, 1),
            "baro": 101.3,
            "advance": round(12 + 20 * (1 - throttle), 1),
            "pulse_width": round(2.1 + 9.5 * throttle, 2),
            "battery_voltage": round(13.8 + 0.15 * math.sin(index / 9), 2),
            "boost_target": round(100 + 90 * throttle, 1),
            "boost_duty": round(75 * throttle, 1),
            "vss": round(10 + 155 * run, 1),
        })

    return rows
