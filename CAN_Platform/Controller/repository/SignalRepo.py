import sqlite3

from domain.Signal import Signal

conn = sqlite3.connect('ecu_data.db')

def create_signal(can_frame_id, signal_name, signal_value, signal_unit):
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO signals (frame_id, signal_name, value, unit) 
                   VALUES (?,?,?,?)''',
                   (can_frame_id, signal_name, signal_value, signal_unit))

    signal_id = cursor.lastrowid
    conn.commit()
    return Signal(signal_id, can_frame_id, signal_name, signal_value, signal_unit)

