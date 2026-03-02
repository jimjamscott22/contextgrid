@echo off
title ContextGrid
cd /d "%~dp0"

echo Starting ContextGrid...
echo.

:: Start API server in background
start "ContextGrid API" /min cmd /c "uv run uvicorn api.server:app --host 0.0.0.0 --port 8000"

:: Wait for API to be ready
echo Waiting for API server...
:wait
timeout /t 1 /nobreak >nul
curl -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 goto wait
echo API server ready.

:: Start Web UI in background
start "ContextGrid Web" /min cmd /c "uv run uvicorn web.app:app --host 127.0.0.1 --port 8081"

:: Brief pause then open browser
timeout /t 2 /nobreak >nul
start http://localhost:8081

echo.
echo ContextGrid is running, Jamie, go add some projects!
echo   API:  http://localhost:8000
echo   Web:  http://localhost:8081
echo.
echo Close this window to kill it (or close the minimized windows).
pause
