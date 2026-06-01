from bluezero import peripheral
from gi.repository import GLib

from extra.signal_cache import signal_cache

SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
CHAR_UUID    = 'abcdef01-1234-5678-1234-56789abcdef0'

NOTIFY_INTERVAL_MS = 200  # 5 Hz


class BLETlmServer:
    def __init__(self):
        self._char = None         # localGATT.Characteristic, set on subscribe
        self._timer_id = None     # GLib timer source ID

        self.ble = peripheral.Peripheral(
            adapter_address='88:A2:9E:B1:52:A9',
            local_name='Vehicular_Monitor',
        )

        self.ble.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)

        self.ble.add_characteristic(
            srv_id=1,
            chr_id=1,
            uuid=CHAR_UUID,
            value=[],
            notifying=False,
            flags=['read', 'notify'],
            read_callback=self.read_callback,
            # bluezero 0.9.x calls notify_callback(notifying: bool,
            # characteristic: localGATT.Characteristic) on subscribe/unsubscribe.
            # It does NOT call it periodically — we drive that ourselves via GLib.
            notify_callback=self.notify_cb,
        )

    def read_callback(self):
        """Called when the Android client reads the characteristic explicitly."""
        return list(signal_cache.get_formatted_string().encode('utf-8'))

    def notify_cb(self, notifying: bool, characteristic) -> None:
        """Called by bluezero when the Android subscribes or unsubscribes."""
        if notifying:
            self._char = characteristic
            self._timer_id = GLib.timeout_add(NOTIFY_INTERVAL_MS, self._send_notify)
        else:
            self._char = None
            if self._timer_id is not None:
                GLib.source_remove(self._timer_id)
                self._timer_id = None

    def _send_notify(self) -> bool:
        """GLib timer callback — pushes one BLE notification then reschedules."""
        if self._char is None or not self._char.is_notifying:
            self._timer_id = None
            return False  # remove timer
        self._char.set_value(
            list(signal_cache.get_formatted_string().encode('utf-8'))
        )
        return True  # keep timer running

    def start(self) -> None:
        print("Starting BLE server ...")
        self.ble.publish()  # blocks – runs the D-Bus / GLib main loop


# Singleton
ble_server = BLETlmServer()