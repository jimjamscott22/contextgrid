#!/usr/bin/env bash
# Build the React SPA frontend so the FastAPI server can serve it.
# After running this, start the API server normally and visit it directly —
# the SPA will be served from /, with /api/* untouched.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
FRONTEND_DIR="${ROOT_DIR}/frontend"

if [ ! -d "${FRONTEND_DIR}" ]; then
  echo "frontend/ directory not found at ${FRONTEND_DIR}" >&2
  exit 1
fi

cd "${FRONTEND_DIR}"

if [ ! -d node_modules ]; then
  echo "Installing npm dependencies..."
  npm install --no-audit --no-fund
fi

echo "Building React SPA..."
npm run build

echo
echo "Frontend built. The API server will now serve it from /"
echo "  → start with: uv run uvicorn api.server:app --host 0.0.0.0 --port 8003"
