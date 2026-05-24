import sqlite3
from contextlib import closing


DB_PATH = "ecu_data.db"


def database_setup():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time REAL NOT NULL,
            end_time REAL,
            description TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS can_frames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER REFERENCES sessions(id),
            timestamp REAL NOT NULL,
            can_id INTEGER NOT NULL,
            dlc INTEGER,
            data TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frame_id INTEGER REFERENCES can_frames(id),
            signal_name TEXT,
            value REAL,
            unit TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            rpm INTEGER,
            sync INTEGER,
            engine_status INTEGER,
            map REAL,
            baro REAL,
            tps REAL,
            iat REAL,
            clt REAL,
            afr REAL,
            ego_correction REAL,
            pulse_width REAL,
            ve REAL,
            advance REAL,
            dwell REAL,
            battery_voltage REAL,
            boost_target REAL,
            boost_duty REAL,
            vss REAL,
            fan INTEGER,
            fp INTEGER,
            boost_cut INTEGER
        )
        """)

        conn.commit()


def database_cleanup():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM signals")
        cursor.execute("DELETE FROM vehicle_state")
        cursor.execute("DELETE FROM can_frames")
        cursor.execute("DELETE FROM sessions")
        conn.commit()


def database_teardown():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS sessions")
        cursor.execute("DROP TABLE IF EXISTS can_frames")
        cursor.execute("DROP TABLE IF EXISTS signals")
        cursor.execute("DROP TABLE IF EXISTS vehicle_state")
        conn.commit()
