import sqlite3
import time

from domain.Session import Session

def create_session(description="Test Session"):
    conn = sqlite3.connect('ecu_data.db')
    cursor = conn.cursor()

    start_time = time.time()

    cursor.execute('''INSERT INTO sessions (start_time, description) 
                      VALUES (?,?)''',
                   (start_time, description))

    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return Session(session_id, start_time, description)

