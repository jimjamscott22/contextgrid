@echo off
title ContextGrid
cd /d "%~dp0"

echo Starting ContextGrid at http://127.0.0.1:8003/
uv run uvicorn api.server:app --host 127.0.0.1 --port 8003
if errorlevel 1 pause
