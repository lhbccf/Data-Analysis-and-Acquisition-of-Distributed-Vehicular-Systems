#!/bin/bash
set -euo pipefail

APP_DIR="/home/goncalo/Desktop/Data-Analysis-and-Acquisition-of-Distributed-Vehicular-Systems/CAN_Platform/Controller"
LOG_PREFIX="[can-controller]"

cd "$APP_DIR"

CONFIG_TYPE=$(python3 - <<'PY'
import json
with open('config.json') as f:
    print(json.load(f).get('type', ''))
PY
)

CONFIG_MODE=$(python3 - <<'PY'
import json
with open('config.json') as f:
    print(json.load(f).get('mode', ''))
PY
)

CAN_PORT=$(python3 - <<'PY'
import json
with open('config.json') as f:
    print(json.load(f).get('com', ''))
PY
)

NEXTION_PORT=$(python3 - <<'PY'
import json
with open('config.json') as f:
    print(json.load(f).get('nextion_port', ''))
PY
)

wait_for_device() {
    local device="$1"
    local label="$2"
    local retries="${3:-30}"

    if [ -z "$device" ]; then
        return 0
    fi

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
    python -m pip install pyserial cantools python-can

    if [ "$CONFIG_MODE" = "pi_screen" ]; then
        python -m pip install pyqtgraph PyQt5
    fi
fi

if [ "$CONFIG_TYPE" = "rusefi_can" ]; then
    wait_for_device "$CAN_PORT" "CAN adapter"
fi

if [ "$CONFIG_MODE" = "nextion" ]; then
    wait_for_device "$NEXTION_PORT" "Nextion serial"
fi

export PYTHONUNBUFFERED=1
exec python main.py
