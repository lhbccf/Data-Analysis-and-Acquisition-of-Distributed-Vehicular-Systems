import serial
import struct
import sys
from pathlib import Path


CONTROLLER_DIR = Path(__file__).resolve().parents[2]
if str(CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIR))

import cantools

PORT = "/dev/ttyACM0"
BAUD = 2000000

# carregar DBC
db = cantools.database.load_file(str(CONTROLLER_DIR / "rusefi.dbc"))

ser = serial.Serial(PORT, BAUD, timeout=1)

# ativar binário GVRET
ser.write(bytes([0xE7]))

print("À espera de frames...\n")

while True:

    start = ser.read(1)

    if not start:
        continue

    if start[0] != 0xF1:
        continue

    cmd = ser.read(1)

    if not cmd:
        continue

    cmd = cmd[0]

    if cmd == 0x00:

        header = ser.read(9)

        if len(header) < 9:
            continue

        timestamp = struct.unpack('<I', header[0:4])[0]

        canid_raw = struct.unpack('<I', header[4:8])[0]

        dlc_bus = header[8]

        dlc = dlc_bus & 0x0F

        data = ser.read(dlc)

        ser.read(1)

        canid = canid_raw & 0x1FFFFFFF

        try:
            # procurar mensagem na DBC
            message = db.get_message_by_frame_id(canid)

            # decodificar sinais
            decoded = message.decode(data)

            print(f"\n{message.name}")

            for signal, value in decoded.items():
                print(f"  {signal}: {value}")

        except:
            # frame desconhecida
            print(
                f"ID:{hex(canid)} DATA:{data.hex(' ')}"
            )
