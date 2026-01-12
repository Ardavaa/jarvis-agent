@echo off
echo Starting JARVIS Backend Server...
echo.
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
