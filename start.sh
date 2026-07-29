#!/bin/bash
# Linux/macOS terminal launcher: ./start.sh
cd "$(dirname "$0")"

if command -v python3 &>/dev/null; then PY=python3; else PY=python; fi
echo "Using: $($PY --version)"

if ! $PY -c "import flask" &>/dev/null; then
  echo "Installing Flask..."
  $PY -m pip install --user flask --quiet --disable-pip-version-check || $PY -m pip install flask --quiet
fi

echo "Dashboard: http://127.0.0.1:5000"
$PY app.py
