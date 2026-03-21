import sqlite3

from domain.Signal import Signal

def create_signal(frame_id, signal_name, value, unit):
    conn = sqlite3.connect('ecu_data.db')
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO signals (frame_id, signal_name, value, unit) 
                   VALUES (?,?,?,?)''',
                   (frame_id, signal_name, value, unit))

    signal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return Signal(signal_id, frame_id, signal_name, value, unit)