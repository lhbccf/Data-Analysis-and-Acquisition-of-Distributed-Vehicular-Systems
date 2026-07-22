# Vehicular Data Analysis (Android App)

Android companion app for the [CAN Platform Controller](../Controller/README.md).
It connects to the controller over Bluetooth Low Energy (BLE), shows live ECU
data in real time, and lets the user browse recorded sessions and aggregate
statistics stored on the controller's database.

Written in Kotlin with Jetpack Compose. Package: `com.example.vehiculardataanalysis`.
Min SDK 24, target/compile SDK 36.

## How it works

1. `MenuActivity` (the launcher activity) requests the Bluetooth/location
   runtime permissions and scans for nearby BLE peripherals.
2. Selecting a device opens `DeviceMenuActivity`, which links to:
   - **Live Data** (`DataDisplayActivity`) — real-time sensor stream.
   - **Sessions Information** (`SessionMenuActivity` / `SessionStatsActivity`) — recorded sessions and their stats.
   - **Overall Statistics** (`OverallStatsActivity`) — aggregate stats across all sessions.
   - **Device Information** (`AboutDeviceActivity`).
3. `BleManager` owns the Android Bluetooth stack (scanning, bonded devices,
   GATT connection). `BleRepository` wraps it behind flows (`scannedDevices`,
   `canData`, `sessionData`). `BleViewModel`/`SessionViewModel` expose that
   data to the Compose screens as `StateFlow`.

All activities extend `BaseActivity`, which standardizes lifecycle logging and
navigation between screens.

## BLE protocol

The app talks to a single GATT service exposing three characteristics, matching
the controller's `transmitter/bluetooth_transmitter.py`:

| Characteristic | Flags | Purpose |
| --- | --- | --- |
| Sensor data | read, notify | CSV payload of 13 fields at 5 Hz: `rpm,temp,afr,tps,map,battery,dwell,timing,vss,iat,ego_correction,ve,sync` |
| Session request | write | Commands: `GET_SESSIONS`, `GET_SESSION:<id>`, `CREATE_SESSION`, `END_SESSION` |
| Session response | read, notify | Session list / stats sent back line by line |

Service and characteristic UUIDs are hardcoded in `BleManager.kt` and must
match the controller.

## Mock mode

The app has a hidden mock "Test Device" for exercising the UI without a real
controller/ECU connected.

**To unlock it:** on the main menu, long-press (hold) the info (ⓘ) button in
the top-right corner. This reveals a "Test Device" entry (tagged `Mock`) in
the device list. Long-pressing again hides it. Selecting it behaves like a
normal device, but all data comes from generators instead of BLE:

- `DataDisplayActivity` calls `BleViewModel.startMockData()` — a continuous
  stream of randomized sensor values.
- Session/statistics screens call `SessionViewModel.startMockSessions()`,
  `startMockCreateSession()`, `startMockEndSession()`, and
  `startMockSessionStats()` — simulated session data.

## Tests

Unit tests live under `app/src/test/java/.../tests` (JUnit + MockK +
coroutines-test), covering `BleViewModel` and `SessionViewModel` parsing and
state logic.

```bash
./gradlew test
```

## Building

```bash
./gradlew assembleDebug
```

Requires Android Studio / an Android SDK with API level 36 installed.
