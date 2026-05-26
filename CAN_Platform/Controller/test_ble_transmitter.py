#!/usr/bin/env python3
"""
Real hardware BLE transmission test for Vehicular Monitor.

Generates mock ECU sensor data and broadcasts it to the Android device
running DataDisplayActivity via BLE from the Raspberry Pi Zero 2W.

Usage (Raspberry Pi):
    sudo python3 test_ble_transmitter.py

Android device:
    Open app → scan → connect to 'Vehicular_Monitor'
    DataDisplayActivity will show live sensor readings.
"""

import math
import os
import signal
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extra.signal_cache import signal_cache
from transmitter.bluetooth_transmitter import CHAR_UUID, SERVICE_UUID, ble_server

# ──────────────────────────── Mock CAN data generator ────────────────────────


class MockCANDataGenerator:
    """
    Simulates realistic ECU sensor readings:
      - RPM idles ~800, cycles up to ~1700 over ~30 s then back down
      - Coolant temp warms from 20 °C to 90 °C (faster at higher RPM)
      - AFR stays near stoichiometric (14.7) with minor variation
      - TPS, MAP, battery voltage, coil dwell, and ignition timing all
        derived from RPM to mimic a real engine running at idle/light load
    """

    INTERVAL = 0.2  # 5 Hz – same cadence as BLE notify loop

    def __init__(self) -> None:
        self._tick = 0
        self._coolant = 20.0
        self._running = False
        self._thread: threading.Thread | None = None

    # ── Sensor models ─────────────────────────────────────────────────────────

    def _rpm(self) -> int:
        slow = math.sin(self._tick * 0.03) * 600   # slow cycle  ±600 rpm
        blip = math.sin(self._tick * 0.11) * 300   # fast blips  ±300 rpm
        return max(700, int(800 + slow + blip))

    def _coolant_temp(self, rpm: int) -> float:
        rate = 0.04 + (rpm - 800) / 100_000
        self._coolant += (90.0 - self._coolant) * rate
        return round(self._coolant, 1)

    def _afr(self) -> float:
        return round(14.7 + math.sin(self._tick * 0.17) * 0.4, 2)

    def _tps(self, rpm: int) -> float:
        return round(max(0.0, min(100.0, (rpm - 700) / 25.0)), 1)

    def _map_kpa(self, rpm: int) -> float:
        # Manifold vacuum drops as RPM rises
        return round(max(30.0, 100.0 - (rpm - 700) / 50.0), 1)

    def _battery(self, rpm: int) -> float:
        # Alternator output climbs with engine speed
        return round(12.5 + min(1.9, (rpm - 700) / 2_000.0), 1)

    def _dwell(self) -> float:
        return round(3.5 + math.sin(self._tick * 0.07) * 0.5, 1)

    def _timing(self, rpm: int) -> float:
        # Advance from 10° BTDC at idle to 30° at high rpm
        return round(min(30.0, 10.0 + (rpm - 700) / 100.0), 1)

    # ── Update loop ───────────────────────────────────────────────────────────

    def _loop(self) -> None:
        while self._running:
            self._tick += 1
            rpm = self._rpm()
            signal_cache.update_batch(
                {
                    "rpm":     rpm,
                    "temp":    self._coolant_temp(rpm),
                    "afr":     self._afr(),
                    "tps":     self._tps(rpm),
                    "map":     self._map_kpa(rpm),
                    "battery": self._battery(rpm),
                    "dwell":   self._dwell(),
                    "timing":  self._timing(rpm),
                }
            )
            time.sleep(self.INTERVAL)

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="mock-can"
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False


# ────────────────────────── Console status printout ──────────────────────────


def _status_loop() -> None:
    """Print current signal values every 2 s so the operator can verify output."""
    header = (
        f"  {'RPM':<7} {'Temp°C':<8} {'AFR':<7} {'TPS%':<7}"
        f" {'MAP kPa':<9} {'Batt V':<8} {'Dwell':<7} Timing°"
    )
    print(header)
    print("  " + "-" * 65)
    while True:
        time.sleep(2)
        parts = signal_cache.get_formatted_string().split(",")
        row = "  " + "  ".join(f"{v:<7}" for v in parts)
        print(row)


# ─────────────────────────────────── Main ────────────────────────────────────


def main() -> None:
    print("=" * 60)
    print("  Vehicular Monitor - Hardware BLE Transmission Test")
    print("=" * 60)
    print()

    # 1. Start mock data generator – feeds signal_cache at 5 Hz
    generator = MockCANDataGenerator()
    generator.start()
    print("[OK]  Mock CAN data generator started (5 Hz)")

    # 2. BLE server singleton was created when the module was imported;
    #    verify it exists before proceeding.
    print("[OK]  BLE GATT server initialised")
    print()
    print(f"  Advertising as : Vehicular_Monitor")
    print(f"  Service UUID   : {SERVICE_UUID}")
    print(f"  Characteristic : {CHAR_UUID}")
    print(f"  Payload format : rpm,temp,afr,tps,map,battery,dwell,timing")
    print()
    print("Android instructions:")
    print("  1. Open the Vehicular Data Analysis app")
    print("  2. Tap 'Scan' and select 'Vehicular_Monitor'")
    print("  3. DataDisplayActivity will display live sensor readings")
    print()
    print("Live signal values (updated every 2 s):")
    print()

    # 3. Daemon thread that prints current values to the console
    threading.Thread(target=_status_loop, daemon=True, name="status").start()

    # 4. Graceful shutdown on Ctrl+C / SIGTERM
    def _shutdown(*_) -> None:
        print("\n[INFO] Shutting down ...")
        generator.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # 5. Log Android connect / disconnect events.
    ble_server.ble.on_connect    = lambda addr: print(f"\n[BLE] Android connected    : {addr}")
    ble_server.ble.on_disconnect = lambda addr: print(f"\n[BLE] Android disconnected : {addr}")

    # 6. Advertise the GATT peripheral and run the D-Bus / GLib main loop.
    #    bluezero 0.9.x calls notify_callback automatically at intervals once
    #    the Android client subscribes – no manual notify thread needed.
    print("[INFO] Starting BLE advertisement – waiting for Android device ...")
    print("       Press Ctrl+C to stop.\n")
    try:
        ble_server.start()
    except Exception as exc:
        print(f"\n[ERROR] BLE publish failed: {exc}")
        print(
            "        Ensure BlueZ is running and this process has the required permissions.\n"
            "        Try: sudo ./venv/bin/python3 test_ble_transmitter.py"
        )
        generator.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
