from bluezero import peripheral
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
        """Callback when client reads the characteristic.
        Format: rpm,temp,afr,tps,map,battery,dwell,timing
        """
        formatted_data = signal_cache.get_formatted_string()
        return formatted_data.encode('utf-8')

    def notify_loop(self):
        """Periodic notification loop - sends data every 200ms (5 updates/sec).
        This matches the mobile app's mock data update frequency.
        """
        while True:
            try:
                # Update characteristic with latest data
                self.ble.update_characteristic_value(1, 1)
                time.sleep(0.2)  # 200ms = 5 updates per second
            except Exception as e:
                print(f"Error in notify_loop: {e}")
                time.sleep(0.2)

    def start(self):
        print("Starting BLE server...")
        self.ble.publish()

        threading.Thread(target=self.notify_loop, daemon=True).start()

        print("BLE running as Vehicular_Monitor")
        print(f"Service UUID: {SERVICE_UUID}")
        print(f"Characteristic UUID: {CHAR_UUID}")
        print("Data format: rpm,temp,afr,tps,map,battery,dwell,timing")


# Singleton
ble_server = BLETlmServer()