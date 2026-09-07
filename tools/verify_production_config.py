#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server import build_deployment_status  # noqa: E402


def main() -> int:
    status = build_deployment_status()
    print(json.dumps({"deployment": status}, ensure_ascii=False, indent=2))
    return 0 if status["production_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
