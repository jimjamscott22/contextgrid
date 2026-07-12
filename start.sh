#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_URL="http://127.0.0.1:8003/api/health"
FRONTEND_URL="http://127.0.0.1:5173"
STARTUP_TIMEOUT_SECONDS=30

export PATH="$HOME/.local/bin:$PATH"

if ! command -v npm >/dev/null 2>&1; then
    export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
    if [[ -s "$NVM_DIR/nvm.sh" ]]; then
        # shellcheck source=/dev/null
        . "$NVM_DIR/nvm.sh"
    fi
fi

require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Required command not found: $1" >&2
        exit 1
    fi
}

for required_command in uv npm curl xdg-open; do
    require_command "$required_command"
done

api_pid=""
frontend_pid=""

cleanup() {
    for pid in "$api_pid" "$frontend_pid"; do
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done

    for pid in "$api_pid" "$frontend_pid"; do
        if [[ -n "$pid" ]]; then
            wait "$pid" 2>/dev/null || true
        fi
    done
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

wait_for_services() {
    local attempt

    for ((attempt = 1; attempt <= STARTUP_TIMEOUT_SECONDS; attempt++)); do
        if ! kill -0 "$api_pid" 2>/dev/null; then
            echo "ContextGrid API exited before it became ready." >&2
            return 1
        fi

        if ! kill -0 "$frontend_pid" 2>/dev/null; then
            echo "ContextGrid frontend exited before it became ready." >&2
            return 1
        fi

        if curl --fail --silent --output /dev/null "$API_URL" \
            && curl --fail --silent --output /dev/null "$FRONTEND_URL"; then
            return 0
        fi

        sleep 1
    done

    echo "ContextGrid did not become ready within ${STARTUP_TIMEOUT_SECONDS} seconds." >&2
    return 1
}

echo "Starting ContextGrid API..."
(cd "$PROJECT_ROOT" && exec uv run uvicorn api.server:app --host 0.0.0.0 --port 8003) &
api_pid=$!

echo "Starting ContextGrid frontend..."
(cd "$PROJECT_ROOT/frontend" && exec npm run dev) &
frontend_pid=$!

if ! wait_for_services; then
    exit 1
fi

echo "Opening ContextGrid in your browser..."
xdg-open "$FRONTEND_URL"

wait -n "$api_pid" "$frontend_pid"
