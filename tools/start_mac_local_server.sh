#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -d /tmp/yijin-venv ]; then
  /usr/bin/python3 -m venv /tmp/yijin-venv
  source /tmp/yijin-venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
else
  source /tmp/yijin-venv/bin/activate
fi

export BAZI_PORT="${BAZI_PORT:-8787}"
python server.py
