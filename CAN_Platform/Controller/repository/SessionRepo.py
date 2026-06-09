import sqlite3
import time
from contextlib import closing

from domain.Session import Session
from repository.database.database_manager import DB_PATH


def _row_to_session(row):
    session = Session(row[0], row[1], row[3])
    session.end_time = row[2]
    return session


def create_session(description="Test Session"):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        start_time = time.time()

        cursor.execute(
            "INSERT INTO sessions (start_time, description) VALUES (?, ?)",
            (start_time, description),
        )

        session_id = cursor.lastrowid
        conn.commit()

    return Session(session_id, start_time, description)


def end_session(session_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sessions SET end_time = ? WHERE id = ?",
            (time.time(), session_id),
        )
        conn.commit()


def clear_session_frames(session_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM signals WHERE frame_id IN "
            "(SELECT id FROM can_frames WHERE session_id = ?)",
            (session_id,),
        )
        cursor.execute(
            "DELETE FROM can_frames WHERE session_id = ?",
            (session_id,),
        )
        conn.commit()

def get_all_sessions():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, start_time, end_time, description FROM sessions ORDER BY start_time DESC"
        )
        return [_row_to_session(row) for row in cursor.fetchall()]

def get_recent_sessions(limit=5):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, start_time, end_time, description
            FROM sessions
            ORDER BY start_time DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [_row_to_session(row) for row in cursor.fetchall()]


def close_database():
    pass
