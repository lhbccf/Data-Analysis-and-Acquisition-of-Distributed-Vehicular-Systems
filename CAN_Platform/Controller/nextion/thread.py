import serial
import threading
import time
import logging
from extra.signal_cache import signal_cache
from extra.logging_setup import configure_logging

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


def update_nextion(ser, data, max_rpm, shift_point):

    try:
        afr = float(data["afr"])
        afr_gauge = int(((afr - 10) / 10) * 100)

        if afr_gauge < 0:
            afr_gauge = 0
        elif afr_gauge > 100:
            afr_gauge = 100

        bytes_written = send_cmd(
            ser,
            f'rpm.txt="{int(data["rpm"])}"'
        )

        bytes_written += send_cmd(
            ser,
            f'afr.txt="AFR: {data["afr"]:.1f} AFR"'
        )

        bytes_written += send_cmd(
            ser,
            f'clt.txt="CLT: {int(data["clt"])} C"'
        )

        bytes_written += send_cmd(
            ser,
            f'adv.txt="ADV: {data["advance"]:.1f} deg"'
        )

        bytes_written += send_cmd(
            ser,
            f'map.txt="MAP: {data["map"]:.1f} kPa"'
        )

        bytes_written += send_cmd(
            ser,
            f'baro.txt="BARO: {data["baro"]:.1f} kPa"'
        )

        bytes_written += send_cmd(
            ser,
            f'tps.txt="TPS: {data["tps"]:.1f} %"'
        )

        bytes_written += send_cmd(
            ser,
            f'iat.txt="IAT: {int(data["iat"])} C"'
        )

        bytes_written += send_cmd(
            ser,
            f'ego.txt="EGO: {data["ego_correction"]:.0f} %"'
        )

        bytes_written += send_cmd(
            ser,
            f'pw.txt="PW: {data["pulse_width"]:.2f} ms"'
        )

        bytes_written += send_cmd(
            ser,
            f've.txt="VE: {int(data["ve"])} %"'
        )

        bytes_written += send_cmd(
            ser,
            f'dwell.txt="DWELL: {data["dwell"]:.1f} ms"'
        )

        bytes_written += send_cmd(
            ser,
            f'bat.txt="BAT: {data["battery_voltage"]:.1f} V"'
        )

        bytes_written += send_cmd(
            ser,
            f'boost.txt="BOOST: {data["boost_target"]:.1f} kPa"'
        )

        bytes_written += send_cmd(
            ser,
            f'duty.txt="DUTY: {data["boost_duty"]:.0f} %"'
        )

        bytes_written += send_cmd(
            ser,
            f'sync.txt="SYNC: {int(data["sync"])}"'
        )

        bytes_written += send_cmd(
            ser,
            f'engine.txt="ENGINE: {int(data["engine_status"])}"'
        )

        bytes_written += send_cmd(
            ser,
            f'fan.txt="FAN: {int(data["fan"])}"'
        )

        bytes_written += send_cmd(
            ser,
            f'fp.txt="FP: {int(data["fp"])}"'
        )

        bytes_written += send_cmd(
            ser,
            f'boostcut.txt="BOOSTCUT: {int(data["boost_cut"])}"'
        )

        bytes_written += send_cmd(
            ser,
            f'rpmgauge.val="{int((data["rpm"] / max_rpm)*100)}"'
        )

        clt = data["clt"]

        if clt < 60:
            gauge = 0
        elif clt > 120:
            gauge = 100
        else:
            gauge = int(((clt - 60) / 60) * 100)

        bytes_written += send_cmd(
            ser,
            f'cltgauge.val={gauge}'
        )
        bytes_written += send_cmd(
            ser,
            f'afrgauge.val={afr_gauge}'
        )
        bytes_written += send_cmd(
            ser,
            f'vss.txt="VSS: {int(data["vss"])} km/h"'
        )

        if int(data["rpm"]) > shift_point:
            bytes_written += send_cmd(
                ser,
                f'shiftlight.pco="{6400}"'
            )
        else:
            bytes_written += send_cmd(
                ser,
                f'shiftlight.pco="{0}"'
            )

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

    except Exception as e:

        logger.exception(f"NEXTION UPDATE ERROR: {e}")
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

    except Exception as e:

        logger.exception(f"SERIAL INIT ERROR: {e}")
        return

    last_version = None

    while True:

        try:

            data = signal_cache.get_all()
            version = data.get("_version")

            if version != last_version:

                if update_nextion(ser, data, config["redline"], config["shift_point"]):
                    last_version = version

            time.sleep(0.1)

        except Exception as e:

            logger.exception(f"NEXTION ERROR: {e}")

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
