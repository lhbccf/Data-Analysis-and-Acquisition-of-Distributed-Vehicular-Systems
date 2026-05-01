from bluezero import peripheral
import struct
import threading
import time

from extra.signal_cache import signal_cache


SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
CHAR_UUID    = '12345678-1234-5678-1234-56789abcdef1'

class BLETlmServer:
    def __init__(self):
        self.ble = peripheral.Peripheral(
            adapter_addr='00:00:00:00:00:00',
            local_name='Vehicular_Monitor',
        )

        self.ble.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)

        self.ble.add_characteristic(
            srv_id=1,
            chr_id=1,
            uuid=CHAR_UUID,
            value=[],
            notifying=True,
            flags=['read', 'notify'],
            read_callback=self.read_callback
        )

    def read_callback(self):
        data = signal_cache.get_all()

        rpm = data["rpm"]
        temp = data["temp"]
        throttle = data["throttle"]

        return struct.pack('<HhB', rpm, temp, throttle)

    def notify_loop(self):
        while True:
            self.ble.update_characteristic_value(1, 1)
            time.sleep(0.1)

    def start(self):
        print("Starting BLE server...")
        self.ble.publish()

        threading.Thread(target=self.notify_loop, daemon=True).start()

        print("BLE running as Vehicular_Monitor")


# Singleton
ble_server = BLETlmServer()