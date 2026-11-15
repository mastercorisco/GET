#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT/backend"
python3 -m pip install -e ".[dev]" -q
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 4810 &
API_PID=$!

cd "$ROOT/frontend"
npm install --silent
npm run dev &
WEB_PID=$!

trap 'kill $API_PID $WEB_PID 2>/dev/null || true' EXIT
wait