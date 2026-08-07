#!/bin/bash
# Double-click this file to start Lead Finder. No Terminal typing needed.
# (First time: macOS may say "unidentified developer" — right-click this file,
#  choose Open, then click Open again. Only needs doing once.)

cd "$(dirname "$0")"
echo "Starting Lead Finder from: $(pwd)"
echo ""

if command -v python3 &>/dev/null; then
  PY=python3
elif command -v python &>/dev/null; then
  PY=python
else
  echo "Python 3 isn't installed. Get it free from https://www.python.org/downloads/"
  echo "Then double-click this file again."
  read -p "Press Enter to close..."
  exit 1
fi

echo "Using: $($PY --version)"

if ! $PY -c "import flask" &>/dev/null; then
  echo "Installing Flask (one-time, ~10 seconds)..."
  $PY -m pip install --user flask --quiet --disable-pip-version-check
  if ! $PY -c "import flask" &>/dev/null; then
    echo "Flask install failed. Try running manually:  $PY -m pip install flask"
    read -p "Press Enter to close..."
    exit 1
  fi
fi

echo ""
echo "Launching... your browser will open on its own."
echo "The exact address is printed below — port 5000 is often taken on macOS"
echo "by AirPlay Receiver, so the app picks the next free port automatically."
echo ""

# app.py finds a free port and opens the browser itself, so no port is
# hardcoded here — that used to open the wrong address when 5000 was busy.
$PY app.py

read -p "Server stopped. Press Enter to close..."
