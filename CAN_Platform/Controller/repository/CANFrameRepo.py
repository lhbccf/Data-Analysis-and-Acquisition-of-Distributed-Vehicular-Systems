import sqlite3
import time

from domain.CANFrame import CANFrame

def create_can_frame(session_id, can_id, dlc, data):
    conn = sqlite3.connect('ecu_data.db')
    cursor = conn.cursor()

    timestamp = time.time()

    cursor.execute('''INSERT INTO canframes (session_id, timestamp, can_id, dlc, data) 
                      VALUES (?,?,?,?,?)''',
                   (session_id, timestamp, can_id, dlc, data))

    can_frame_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return CANFrame(can_frame_id, session_id, timestamp, can_id, dlc, data)