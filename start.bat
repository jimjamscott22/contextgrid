@echo off
title ContextGrid
cd /d "%~dp0"

echo Starting ContextGrid API...
start cmd /k "title ContextGrid API && uv run uvicorn api.server:app --host 0.0.0.0 --port 8003"

echo Starting ContextGrid Frontend...
start cmd /k "title ContextGrid Frontend && cd frontend && npm run dev"

echo Both servers started.
echo   API:      http://localhost:8003
echo   Frontend: http://localhost:5173
echo.
pause
