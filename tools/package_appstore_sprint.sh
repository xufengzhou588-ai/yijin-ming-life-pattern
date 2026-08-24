#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

find . -name '._*' -type f -delete

mkdir -p dist
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="dist/MING-appstore-sprint-${STAMP}.tar.gz"

COPYFILE_DISABLE=1 LC_ALL=C tar \
  --exclude './.git' \
  --exclude './.DS_Store' \
  --exclude './._*' \
  --exclude './.pytest_cache' \
  --exclude './__pycache__' \
  --exclude './build' \
  --exclude './DerivedData' \
  --exclude './dist' \
  --exclude './backups' \
  -czf "$OUT" \
  .

find . -name '._*' -type f -delete

echo "$OUT"
