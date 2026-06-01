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

def get_signals_by_session_id(session_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT s.id, s.frame_id, s.signal_name, s.value, s.unit 
                          FROM signals s 
                          JOIN can_frames cf ON s.frame_id = cf.id 
                          WHERE cf.session_id=?''', (session_id,))
        rows = cursor.fetchall()
    return [Signal(*row) for row in rows]

def close_database():
    pass
