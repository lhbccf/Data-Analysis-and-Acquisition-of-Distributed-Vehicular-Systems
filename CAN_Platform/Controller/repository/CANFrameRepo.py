import sqlite3
import time

from domain.CANFrame import CANFrame

conn = sqlite3.connect('ecu_data.db')

def create_can_frame(session_id, can_id, dlc, data):
    cursor = conn.cursor()

    timestamp = time.time()

    cursor.execute('''INSERT INTO can_frames (session_id, timestamp, can_id, dlc, data) 
                      VALUES (?,?,?,?,?)''',
                   (session_id, timestamp, can_id, dlc, data))

    can_frame_id = cursor.lastrowid
    conn.commit()
    return CANFrame(can_frame_id, session_id, timestamp, can_id, dlc, data)

def get_list_can_frames_by_session(session_id):
    cursor = conn.cursor()

    cursor.execute('''SELECT id, session_id, timestamp, can_id, dlc, data 
                      FROM canframes WHERE session_id=?''', (session_id,))
    rows = cursor.fetchall()

    can_frames = []
    for row in rows:
        can_frame = CANFrame(row[0], row[1], row[2], row[3], row[4], row[5])
        can_frames.append(can_frame)
    return can_frames


def get_latest_can_frame_by_session(session_id):
    cursor = conn.cursor()

    cursor.execute('''SELECT id, session_id, timestamp, can_id, dlc, data 
                      FROM canframes WHERE session_id=? ORDER BY timestamp DESC LIMIT 1''', (session_id,))
    row = cursor.fetchone()

    if row:
        return CANFrame(row[0], row[1], row[2], row[3], row[4], row[5])
    return None

def delete_can_frames_by_session(session_id):
    cursor = conn.cursor()

    cursor.execute('''DELETE FROM canframes WHERE session_id=?''', (session_id,))
    conn.commit()

def delete_all_can_frames():
    cursor = conn.cursor()

    cursor.execute('''DELETE FROM canframes''')
    conn.commit()
