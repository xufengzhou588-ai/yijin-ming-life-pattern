#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

unset BAZI_DEMO_UNLOCK
export MING_PRO_MODE=free_first
export BAZI_PORT="${BAZI_PORT:-8787}"

echo "Starting MING free-first local test server..."
echo "Open: http://127.0.0.1:${BAZI_PORT}/app"

bash tools/start_mac_local_server.sh
