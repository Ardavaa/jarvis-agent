@echo off
echo ========================================
echo Starting JARVIS Backend
echo ========================================
echo.

cd backend
uv run uvicorn app.main:app --reload --port 8000

echo.
pause
