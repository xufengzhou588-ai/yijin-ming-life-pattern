#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== Cleaning AppleDouble metadata =="
find . -name '._*' -type f -delete

echo "== Python environment =="
rm -rf /tmp/yijin-venv
/usr/bin/python3 -m venv /tmp/yijin-venv
source /tmp/yijin-venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pytest

echo "== Python tests =="
PYTHONPATH="$ROOT" python -m pytest -q

echo "== HTTP smoke test =="
BAZI_PORT=8787 python server.py >/tmp/yijin-server.out 2>/tmp/yijin-server.err &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT

for _ in 1 2 3 4 5; do
  if curl -fsS http://127.0.0.1:8787/api/entitlement >/tmp/yijin-entitlement.json; then
    break
  fi
  sleep 1
done

curl -fsSI http://127.0.0.1:8787/ >/dev/null
curl -fsSI http://127.0.0.1:8787/app >/dev/null
curl -fsSI http://127.0.0.1:8787/legal/privacy >/dev/null
curl -fsSI http://127.0.0.1:8787/legal/terms >/dev/null
curl -fsSI http://127.0.0.1:8787/support >/dev/null
curl -fsSI http://127.0.0.1:8787/legal/methodology >/dev/null
curl -fsS http://127.0.0.1:8787/api/system/status >/tmp/yijin-system-status.json
curl -fsS -H 'Cookie: bazi_native_pro=1' http://127.0.0.1:8787/api/entitlement >/tmp/yijin-native-entitlement.json

if ! grep -q '"system_version": "2026.08.21"' /tmp/yijin-system-status.json; then
  echo "system status endpoint did not expose expected data policy version"
  cat /tmp/yijin-system-status.json
  exit 1
fi

if ! grep -q '"is_pro": true' /tmp/yijin-native-entitlement.json; then
  echo "native entitlement cookie did not unlock Pro"
  cat /tmp/yijin-native-entitlement.json
  exit 1
fi

demo_status="$(
  curl -sS -o /tmp/yijin-demo-unlock.json -w '%{http_code}' \
    -X POST http://127.0.0.1:8787/api/entitlement/demo-unlock
)"

if [[ "$demo_status" != "403" ]]; then
  echo "demo unlock should be disabled by default, got HTTP $demo_status"
  cat /tmp/yijin-demo-unlock.json
  exit 1
fi

echo "== Xcode simulator build =="
xcodebuild \
  -quiet \
  -project MINGLifePattern.xcodeproj \
  -scheme MINGLifePattern \
  -configuration Debug \
  -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO \
  build

echo "== Verification complete =="
