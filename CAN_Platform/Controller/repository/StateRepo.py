import sqlite3
import time
from contextlib import closing

from domain.VehicleState import VehicleState
from repository.database.database_manager import DB_PATH


STATE_COLUMNS = (
    "session_id",
    "rpm",
    "sync",
    "engine_status",
    "map",
    "baro",
    "tps",
    "iat",
    "clt",
    "afr",
    "ego_correction",
    "pulse_width",
    "ve",
    "advance",
    "dwell",
    "battery_voltage",
    "boost_target",
    "boost_duty",
    "vss",
    "fan",
    "fp",
    "boost_cut",
)


def create_vehicle_state(state):
    timestamp = time.time()
    values = (
        state.get("session_id"),
        state.get("rpm", 0),
        int(state.get("sync", 0)),
        int(state.get("engine_status", 0)),
        state.get("map", 0),
        state.get("baro", 0),
        state.get("tps", 0),
        state.get("iat", 0),
        state.get("clt", 0),
        state.get("afr", 0),
        state.get("ego_correction", 0),
        state.get("pulse_width", 0),
        state.get("ve", 0),
        state.get("advance", 0),
        state.get("dwell", 0),
        state.get("battery_voltage", 0),
        state.get("boost_target", 0),
        state.get("boost_duty", 0),
        state.get("vss", 0),
        int(state.get("fan", False)),
        int(state.get("fp", False)),
        int(state.get("boost_cut", False)),
    )

    placeholders = ", ".join("?" for _ in STATE_COLUMNS)
    columns = ", ".join(STATE_COLUMNS)

    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO vehicle_state (timestamp, {columns})
            VALUES (?, {placeholders})
            """,
            (timestamp, *values),
        )
        vehicle_state_id = cursor.lastrowid
        conn.commit()

    return VehicleState(vehicle_state_id, timestamp, state)


def get_all_vehicle_states():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehicle_state ORDER BY timestamp ASC")
        return cursor.fetchall()


def get_latest_vehicle_state():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM vehicle_state ORDER BY timestamp DESC LIMIT 1"
        )
        return cursor.fetchone()


def get_vehicle_states_by_session_id(session_id, signals):
    allowed_columns = {"timestamp", *STATE_COLUMNS}
    selected_signals = [
        signal for signal in signals
        if signal in allowed_columns and signal != "session_id"
    ]

    if not selected_signals:
        return []

    columns = ["timestamp", *selected_signals]
    column_sql = ", ".join(columns)

    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT {column_sql}
            FROM vehicle_state
            WHERE session_id = ?
            ORDER BY timestamp ASC
            """,
            (session_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_aggregate_vehicle_stats():
    """
    Returns (avg_rpm, max_rpm, avg_clt, max_vss) across all recorded vehicle states.
    Zero-value RPM rows are excluded from the average to avoid idle noise skewing results.
    Returns (0.0, 0, 0.0, 0.0) when no data exists.
    """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COALESCE(AVG(CASE WHEN rpm > 0 THEN rpm END), 0.0),
                COALESCE(MAX(rpm), 0),
                COALESCE(AVG(CASE WHEN clt > 0 THEN clt END), 0.0),
                COALESCE(MAX(vss), 0.0)
            FROM vehicle_state
        """)
        row = cursor.fetchone()
        return row if row else (0.0, 0, 0.0, 0.0)


def get_session_vehicle_stats(session_id):
    """
    Returns (avg_rpm, max_rpm, avg_clt, max_vss) for a specific session.
    Zero-value RPM rows are excluded from the average.
    Returns (0.0, 0, 0.0, 0.0) when no data exists for the session.
    """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COALESCE(AVG(CASE WHEN rpm > 0 THEN rpm END), 0.0),
                COALESCE(MAX(rpm), 0),
                COALESCE(AVG(CASE WHEN clt > 0 THEN clt END), 0.0),
                COALESCE(MAX(vss), 0.0)
            FROM vehicle_state
            WHERE session_id = ?
        """, (session_id,))
        row = cursor.fetchone()
        return row if row else (0.0, 0, 0.0, 0.0)


def delete_all_vehicle_states():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vehicle_state")
        conn.commit()


def close_database():
    pass
