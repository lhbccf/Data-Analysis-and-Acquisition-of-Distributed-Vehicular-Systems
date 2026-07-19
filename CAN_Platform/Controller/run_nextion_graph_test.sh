#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

cd "$SCRIPT_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo "[nextion-graph-test] creating virtual environment"
    python3 -m venv "$VENV_DIR" --system-site-packages
fi

source "$VENV_DIR/bin/activate"

if ! python -c "import serial" 2>/dev/null; then
    echo "[nextion-graph-test] installing pyserial"
    python -m pip install pyserial
fi

echo "[nextion-graph-test] generating and sending graph"
exec python tests/integration/test_nextion_graph.py "$@"
