#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "Starting ContextGrid API..."
echo

uv run uvicorn api.server:app --host 0.0.0.0 --port 8003
