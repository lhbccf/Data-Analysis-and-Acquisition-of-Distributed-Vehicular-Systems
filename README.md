# Data Analysis and Acquisition of Distributed Vehicular Systems

A modular CAN-based data acquisition and analysis platform for distributed
vehicular systems, built for motorsport/enthusiast use
around a Raspberry Pi controller and a companion Android app.

The project has two modules:

- [CAN Platform Controller](CAN_Platform/Controller/README.md) — reads ECU data
  from CAN/GVRET or Speeduino serial, decodes it into a normalized vehicle
  state, drives a Nextion or PyQt display, persists raw CAN frames and
  periodic vehicle state snapshots to SQLite, and broadcasts live data over
  Bluetooth Low Energy.

- [Vehicular Data Analysis](CAN_Platform/Mobile_App/VehicularDataAnalysis/README.md) — an Android app that
  connects to the controller over BLE to show live sensor data and session
  history.
