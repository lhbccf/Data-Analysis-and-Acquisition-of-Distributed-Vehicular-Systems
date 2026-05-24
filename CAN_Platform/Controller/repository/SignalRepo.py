import sqlite3
from contextlib import closing

from domain.Signal import Signal
from repository.database.database_manager import DB_PATH


def create_signal(can_frame_id, signal_name, signal_value, signal_unit):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO signals (frame_id, signal_name, value, unit)
            VALUES (?, ?, ?, ?)
            """,
            (can_frame_id, signal_name, signal_value, signal_unit),
        )

        signal_id = cursor.lastrowid
        conn.commit()

    return Signal(signal_id, can_frame_id, signal_name, signal_value, signal_unit)


def close_database():
    pass
