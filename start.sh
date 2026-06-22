#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

cleanup() {
    kill "$api_pid" "$frontend_pid" 2>/dev/null
    wait "$api_pid" "$frontend_pid" 2>/dev/null
}
trap cleanup EXIT INT TERM

echo "Starting ContextGrid API..."
uv run uvicorn api.server:app --host 0.0.0.0 --port 8003 &
api_pid=$!

echo "Starting ContextGrid frontend..."
cd frontend && npm run dev &
frontend_pid=$!

wait "$api_pid" "$frontend_pid"
