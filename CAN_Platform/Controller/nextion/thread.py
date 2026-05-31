import serial
import threading
import time
import logging
from extra.signal_cache import signal_cache
from extra.logging_setup import configure_logging
from nextion.reader import start_nextion_reader
from repository import SessionRepo

LOG_PATH = configure_logging()
logger = logging.getLogger(__name__)


def send_cmd(ser, cmd):
    payload = cmd.encode()
    terminator = b'\xff\xff\xff'
    written = ser.write(payload)
    written_terminator = ser.write(terminator)

    if hasattr(ser, "flush"):
        ser.flush()

    return (written or len(payload)) + (written_terminator or len(terminator))


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def update_sessions_list(ser, limit=5):
    sessions = SessionRepo.get_recent_sessions(limit)
    text =  r"\r"
    for index, session in sessions:
        text += f"Session {session.id}"
        
    return send_cmd(ser, f'sessions.txt="{text}"')


def update_nextion(ser, data, max_rpm, shift_point):
    try:
        text_commands = [
            f'rpm.txt="{int(data["rpm"])}"',
            f'afr.txt="AFR: {data["afr"]:.1f} AFR"',
            f'clt.txt="CLT: {int(data["clt"])} C"',
            f'adv.txt="ADV: {data["advance"]:.1f} deg"',
            f'map.txt="MAP: {data["map"]:.1f} kPa"',
            f'baro.txt="BARO: {data["baro"]:.1f} kPa"',
            f'tps.txt="TPS: {data["tps"]:.1f} %"',
            f'iat.txt="IAT: {int(data["iat"])} C"',
            f'ego.txt="EGO: {data["ego_correction"]:.0f} %"',
            f'pw.txt="PW: {data["pulse_width"]:.2f} ms"',
            f've.txt="VE: {int(data["ve"])} %"',
            f'dwell.txt="DWELL: {data["dwell"]:.1f} ms"',
            f'bat.txt="BAT: {data["battery_voltage"]:.1f} V"',
            f'boost.txt="BOOST: {data["boost_target"]:.1f} kPa"',
            f'duty.txt="DUTY: {data["boost_duty"]:.0f} %"',
            f'sync.txt="SYNC: {int(data["sync"])}"',
            f'engine.txt="ENGINE: {int(data["engine_status"])}"',
            f'fan.txt="FAN: {int(data["fan"])}"',
            f'fp.txt="FP: {int(data["fp"])}"',
            f'boostcut.txt="BOOSTCUT: {int(data["boost_cut"])}"',
        ]

        rpm_percent = int((data["rpm"] / max_rpm) * 100)
        clt = data["clt"]
        clt_gauge = clamp(int(((clt - 60) / 60) * 100))
        afr_gauge = clamp(int(((float(data["afr"]) - 10) / 10) * 100))
        shiftlight_color = 6400 if int(data["rpm"]) > shift_point else 0

        value_commands = [
            f'rpmgauge.val="{rpm_percent}"',
            f'cltgauge.val={clt_gauge}',
            f'afrgauge.val={afr_gauge}',
            f'vss.txt="VSS: {int(data["vss"])} km/h"',
            f'shiftlight.pco="{shiftlight_color}"',
        ]

        bytes_written = 0
        for command in text_commands + value_commands:
            bytes_written += send_cmd(ser, command)

        logger.info(
            "sent to nextion: version=%s decoded=%s bytes=%s "
            "rpm=%s afr=%.1f clt=%s advance=%.1f map=%.1f tps=%.1f vss=%s",
            data.get("_version"),
            data.get("decoded"),
            bytes_written,
            int(data["rpm"]),
            float(data["afr"]),
            int(data["clt"]),
            float(data["advance"]),
            float(data["map"]),
            float(data["tps"]),
            int(data["vss"]),
        )

        return True

    except Exception as exc:

        logger.exception("NEXTION UPDATE ERROR: %s", exc)
        return False


def nextion_worker(config):
    try:
        ser = serial.Serial(
            port=config["nextion_port"],
            baudrate=config.get("nextion_baud", 115200),
            timeout=1
        )

        time.sleep(2)

        logger.info(
            "Nextion connected on %s @ %s is_open=%s",
            ser.port,
            ser.baudrate,
            ser.is_open,
        )
        start_nextion_reader(ser, config)

    except Exception as exc:

        logger.exception("SERIAL INIT ERROR: %s", exc)
        return

    last_version = None
    last_sessions_update = 0
    sessions_interval = float(config.get("nextion_sessions_interval", 1.0))
    sessions_limit = int(config.get("nextion_sessions_limit", 5))

    while True:

        try:

            data = signal_cache.get_all()
            version = data.get("_version")

            if version != last_version:

                if update_nextion(
                    ser,
                    data,
                    config["redline"],
                    config["shift_point"],
                ):
                    last_version = version

            now = time.time()
            if now - last_sessions_update >= sessions_interval:
                update_sessions_list(ser, sessions_limit)
                last_sessions_update = now

            time.sleep(0.1)

        except Exception as exc:

            logger.exception("NEXTION ERROR: %s", exc)

            time.sleep(1)


def start_nextion(config):

    thread = threading.Thread(
        target=nextion_worker,
        args=(config,),
        daemon=True,
        name="NextionThread"
    )

    thread.start()

    logger.info("Nextion thread started")

    return thread
