import sqlite3
import time
from contextlib import closing

from domain.CANFrame import CANFrame
from repository.database.database_manager import DB_PATH


def create_can_frame(session_id, can_id, dlc, data, timestamp=None):
    timestamp = time.time() if timestamp is None else timestamp

    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO can_frames (session_id, timestamp, can_id, dlc, data)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, timestamp, can_id, dlc, data),
        )

        can_frame_id = cursor.lastrowid
        conn.commit()

    return CANFrame(can_frame_id, session_id, timestamp, can_id, dlc, data)


def get_list_can_frames_by_session(session_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, session_id, timestamp, can_id, dlc, data
            FROM can_frames
            WHERE session_id = ?
            ORDER BY timestamp ASC
            """,
            (session_id,),
        )
        rows = cursor.fetchall()

    return [CANFrame(*row) for row in rows]


def get_latest_can_frame_by_session(session_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, session_id, timestamp, can_id, dlc, data
            FROM can_frames
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (session_id,),
        )
        row = cursor.fetchone()

    return CANFrame(*row) if row else None


def delete_can_frames_by_session(session_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM can_frames WHERE session_id = ?", (session_id,))
        conn.commit()


def delete_all_can_frames():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM can_frames")
        conn.commit()


def close_database():
    pass
