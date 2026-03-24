#!/bin/bash
echo "Starting ContextGrid..."
echo

# Start API server in background
uv run uvicorn api.server:app --host 0.0.0.0 --port 8003 &
API_PID=$!

# Wait for API to be ready
echo "Waiting for API server..."
until curl -s http://localhost:8003/api/health > /dev/null 2>&1; do
    sleep 1
done
echo "API server ready."

# Start Web UI in background
uv run uvicorn web.app:app --host 127.0.0.1 --port 8081 &
WEB_PID=$!

# Brief pause then open browser
sleep 2
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:8081
elif command -v open > /dev/null; then
    open http://localhost:8081
fi

echo
echo "ContextGrid is running, Jamie, go add some projects!"
echo "  API:  http://localhost:8003"
echo "  Web:  http://localhost:8081"
echo
echo "Press Ctrl+C to stop."

# Wait and clean up on exit
trap "kill $API_PID $WEB_PID 2>/dev/null" EXIT
wait
