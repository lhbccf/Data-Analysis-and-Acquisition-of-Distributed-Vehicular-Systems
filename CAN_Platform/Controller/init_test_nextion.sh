#!/bin/bash
set -euo pipefail

APP_DIR="/home/goncalo/Desktop/Data-Analysis-and-Acquisition-of-Distributed-Vehicular-Systems/CAN_Platform/Controller"
LOG_PREFIX="[nextion-test]"

cd "$APP_DIR"

NEXTION_PORT=$(python3 - <<'PY'
import json
with open("config.json") as f:
    print(json.load(f).get("nextion_port", "/dev/serial0"))
PY
)

NEXTION_BAUD=$(python3 - <<'PY'
import json
with open("config.json") as f:
    print(json.load(f).get("nextion_baud", 115200))
PY
)

wait_for_device() {
    local device="$1"
    local label="$2"
    local retries="${3:-30}"

    echo "$LOG_PREFIX waiting for $label at $device"

    for _ in $(seq 1 "$retries"); do
        if [ -e "$device" ]; then
            echo "$LOG_PREFIX found $label at $device"
            return 0
        fi

        sleep 1
    done

    echo "$LOG_PREFIX device not found: $label at $device" >&2
    return 1
}

NEED_INSTALL=0

if [ ! -d "venv" ]; then
    echo "$LOG_PREFIX creating virtualenv"
    python3 -m venv venv --system-site-packages
    NEED_INSTALL=1
fi

source venv/bin/activate

if [ "$NEED_INSTALL" = "1" ]; then
    python -m pip install --upgrade pip
    python -m pip install pyserial
fi

wait_for_device "$NEXTION_PORT" "Nextion serial"

export PYTHONUNBUFFERED=1
exec python tests/integration/test_nextion.py "$NEXTION_PORT" "$NEXTION_BAUD"
