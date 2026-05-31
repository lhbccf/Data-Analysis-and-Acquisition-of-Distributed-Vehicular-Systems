from bluezero import peripheral
from gi.repository import GLib

from extra.signal_cache import signal_cache

SERVICE_UUID               = '12345678-1234-5678-1234-56789abcdef0'
CHAR_UUID                  = 'abcdef01-1234-5678-1234-56789abcdef0'
SESSION_REQUEST_CHAR_UUID  = 'abcdef02-1234-5678-1234-56789abcdef0'
SESSION_RESPONSE_CHAR_UUID = 'abcdef03-1234-5678-1234-56789abcdef0'

NOTIFY_INTERVAL_MS = 200  # 5 Hz


class BLETlmServer:
    def __init__(self):
        self._char = None
        self._timer_id = None
        self._session_response_char = None

        self.ble = peripheral.Peripheral(
            adapter_address='88:A2:9E:B1:52:A9',
            local_name='Vehicular_Monitor',
        )

        self.ble.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)

        # Characteristic 1: sensor data stream (read + notify)
        self.ble.add_characteristic(
            srv_id=1,
            chr_id=1,
            uuid=CHAR_UUID,
            value=[],
            notifying=False,
            flags=['read', 'notify'],
            read_callback=self.read_callback,
            notify_callback=self.notify_cb,
        )

        # Characteristic 2: session request — Android writes "GET_SESSIONS" here
        self.ble.add_characteristic(
            srv_id=1,
            chr_id=2,
            uuid=SESSION_REQUEST_CHAR_UUID,
            value=[],
            notifying=False,
            flags=['write'],
            write_callback=self._session_request_cb,
        )

        # Characteristic 3: session response — Pi notifies one line per session
        self.ble.add_characteristic(
            srv_id=1,
            chr_id=3,
            uuid=SESSION_RESPONSE_CHAR_UUID,
            value=[],
            notifying=False,
            flags=['read', 'notify'],
            read_callback=self._session_response_read_cb,
            notify_callback=self._session_response_notify_cb,
        )

    # ── Sensor data characteristic ───────────────────────────────────────────

    def read_callback(self):
        """Called when the Android client reads the sensor characteristic explicitly."""
        return list(signal_cache.get_formatted_string().encode('utf-8'))

    def notify_cb(self, notifying: bool, characteristic) -> None:
        """Called by bluezero when Android subscribes or unsubscribes to sensor data."""
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
            return False
        self._char.set_value(
            list(signal_cache.get_formatted_string().encode('utf-8'))
        )
        return True

    # ── Session characteristics ──────────────────────────────────────────────

    def _session_response_read_cb(self):
        return list('[]'.encode('utf-8'))

    def _session_response_notify_cb(self, notifying: bool, characteristic) -> None:
        """Called by bluezero when Android subscribes or unsubscribes to session response."""
        if notifying:
            self._session_response_char = characteristic
        else:
            self._session_response_char = None

    def _session_request_cb(self, value, _options) -> None:
        """Called when Android writes a command to the session request characteristic."""
        command = bytes(value).decode('utf-8').strip()
        if command == 'GET_SESSIONS':
            GLib.idle_add(self._send_sessions)

    def _send_sessions(self) -> bool:
        """Fetches all sessions from the DB and sends them one-by-one as BLE notifications."""
        if self._session_response_char is None or not self._session_response_char.is_notifying:
            return False
        try:
            from services import Services
            sessions = Services.get_all_sessions()
            for session in sessions:
                duration = (
                    round(session.end_time - session.start_time, 1)
                    if session.end_time is not None
                    else -1.0
                )
                line = f"{session.id},{session.start_time:.3f},{duration}"
                self._session_response_char.set_value(list(line.encode('utf-8')))
            self._session_response_char.set_value(list('END'.encode('utf-8')))
        except Exception as exc:
            print(f"[ERROR] Failed to send sessions: {exc}")
            err = f'ERR:{exc}'
            if self._session_response_char and self._session_response_char.is_notifying:
                self._session_response_char.set_value(list(err.encode('utf-8')))
        return False

    def start(self) -> None:
        print('Starting BLE server ...')
        self.ble.publish()


# Singleton
ble_server = BLETlmServer()
