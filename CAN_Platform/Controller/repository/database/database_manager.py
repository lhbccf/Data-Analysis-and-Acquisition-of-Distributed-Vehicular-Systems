import sqlite3

def database_setup():
    conn = sqlite3.connect('ecu_data.db')
    cursor = conn.cursor()

    # Sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time bigint not null,
        end_time bigint,
        description varchar(256)
    )
    ''')

    # Raw CAN frames table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS can_frames (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id int references sessions(id),
        timestamp bigint not null,
        can_id bigint not null,
        dlc bigint,
        data varchar(256)
    )
    ''')

    # Decoded signals table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        frame_id int references can_frames(id),
        signal_name varchar(256),
        value bigint,
        unit varchar(256)
    )
    ''')

    conn.commit()
    conn.close()

def database_cleanup():
    conn = sqlite3.connect('ecu_data.db')
    cursor = conn.cursor()

    cursor.execute('''DELETE FROM sessions''')
    cursor.execute('''DELETE FROM can_frames''')
    cursor.execute('''DELETE FROM signals''')

    conn.commit()
    conn.close()

def database_teardown():
    conn = sqlite3.connect('ecu_data.db')
    cursor = conn.cursor()

    cursor.execute('''DROP TABLE IF EXISTS sessions''')
    cursor.execute('''DROP TABLE IF EXISTS can_frames''')
    cursor.execute('''DROP TABLE IF EXISTS signals''')

    conn.commit()
    conn.close()

