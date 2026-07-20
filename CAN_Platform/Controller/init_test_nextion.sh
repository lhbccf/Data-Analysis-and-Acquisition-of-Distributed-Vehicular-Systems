#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

cd "$SCRIPT_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo "[nextion-test] creating virtual environment"
    python3 -m venv "$VENV_DIR" --system-site-packages
fi

source "$VENV_DIR/bin/activate"

if ! python -c "import serial" 2>/dev/null; then
    echo "[nextion-test] installing pyserial"
    python -m pip install pyserial
fi

echo "[nextion-test] sending test values"
exec python tests/integration/test_nextion.py "$@"
