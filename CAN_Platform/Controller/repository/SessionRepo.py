import sqlite3
import time

from domain.Session import Session

conn = sqlite3.connect('ecu_data.db')


def create_session(description="Test Session"):
    cursor = conn.cursor()
    start_time = time.time()
    cursor.execute(
        'INSERT INTO sessions (start_time, description) VALUES (?, ?)',
        (start_time, description)
    )
    session_id = cursor.lastrowid
    conn.commit()
    return Session(session_id, start_time, description)


def end_session(session_id: int):
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE sessions SET end_time = ? WHERE id = ?',
        (time.time(), session_id)
    )
    conn.commit()


def clear_session_frames(session_id: int):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM can_frames WHERE session_id = ?', (session_id,))
    conn.commit()


def get_all_sessions():
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, start_time, end_time, description FROM sessions ORDER BY start_time DESC'
    )
    sessions = []
    for row in cursor.fetchall():
        session_id, start_time, end_time, description = row
        s = Session(session_id, start_time, description)
        s.end_time = end_time
        sessions.append(s)
    return sessions
