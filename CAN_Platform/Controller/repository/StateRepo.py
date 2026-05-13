import sqlite3
import time

from domain.VehicleState import VehicleState

conn = sqlite3.connect(
    'ecu_data.db',
    check_same_thread=False
)


# =========================================================
# CREATE
# =========================================================

def create_vehicle_state(state):

    cursor = conn.cursor()

    timestamp = time.time()

    cursor.execute('''
    INSERT INTO vehicle_state (

        timestamp,

        rpm,
        sync,
        engine_status,

        map,
        baro,
        tps,

        iat,
        clt,

        afr,
        ego_correction,
        pulse_width,
        ve,

        advance,
        dwell,

        battery_voltage,

        boost_target,
        boost_duty,

        vss,

        fan,
        fp,
        boost_cut

    ) VALUES (

        ?,

        ?,?,
        ?,

        ?,?,
        ?,

        ?,?,

        ?,?,
        ?,?,

        ?,?,

        ?,

        ?,?,

        ?,

        ?,?,
        ?

    )
    ''',

    (

        timestamp,

        state.get("rpm", 0),
        int(state.get("sync", 0)),
        int(state.get("engine_status", 0)),

        state.get("map", 0),
        state.get("baro", 0),
        state.get("tps", 0),

        state.get("iat", 0),
        state.get("clt", 0),

        state.get("afr", 0),
        state.get("ego_correction", 0),
        state.get("pulse_width", 0),
        state.get("ve", 0),

        state.get("advance", 0),
        state.get("dwell", 0),

        state.get("battery_voltage", 0),

        state.get("boost_target", 0),
        state.get("boost_duty", 0),

        state.get("vss", 0),

        int(state.get("fan", False)),
        int(state.get("fp", False)),
        int(state.get("boost_cut", False))
    ))

    vehicle_state_id = cursor.lastrowid

    conn.commit()

    return VehicleState(
        vehicle_state_id,
        timestamp,
        state
    )


# =========================================================
# GET ALL
# =========================================================

def get_all_vehicle_states():

    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM vehicle_state
    ORDER BY timestamp ASC
    ''')

    rows = cursor.fetchall()

    return rows


# =========================================================
# GET LATEST
# =========================================================

def get_latest_vehicle_state():

    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM vehicle_state
    ORDER BY timestamp DESC
    LIMIT 1
    ''')

    row = cursor.fetchone()

    return row


# =========================================================
# DELETE ALL
# =========================================================

def delete_all_vehicle_states():

    cursor = conn.cursor()

    cursor.execute('''
    DELETE FROM vehicle_state
    ''')

    conn.commit()
