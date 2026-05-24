# Data Analysis and Acquisition of Distributed Vehicular Systems

This repository contains a CAN/ECU data acquisition platform for distributed
vehicular systems.

The main runtime currently lives in:

- [CAN Platform Controller](CAN_Platform/Controller/README.md)

That controller can read ECU data from CAN/GVRET or Speeduino serial, decode it
into a normalized vehicle state, send it to a UI or Nextion display, and persist
raw CAN frames plus periodic vehicle state snapshots into SQLite.
