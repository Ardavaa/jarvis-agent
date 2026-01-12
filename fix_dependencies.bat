@echo off
echo ========================================
echo Fixing Dependencies for JARVIS
echo ========================================
echo.

echo 1. Updating uv lockfile...
uv lock --upgrade-package websockets

echo 2. Syncing environment...
uv sync

echo.
echo ========================================
echo Dependencies updated! 
echo Websockets should now be version < 14.0
echo ========================================
echo.
pause
