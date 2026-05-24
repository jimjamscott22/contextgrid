@echo off
title ContextGrid API
cd /d "%~dp0"

echo Starting ContextGrid API...
echo.

uv run uvicorn api.server:app --host 0.0.0.0 --port 8003

pause
