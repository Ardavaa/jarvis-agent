@echo off
echo ========================================
echo Starting JARVIS System (All Components)
echo ========================================
echo.

echo 1. Starting MCP Servers...
start "JARVIS MCP Servers" start_mcp_servers.bat
timeout /t 5 /nobreak >nul

echo 2. Starting Backend API...
start "JARVIS Backend" start_backend.bat
timeout /t 5 /nobreak >nul

echo 3. Starting Frontend...
start "JARVIS Frontend" start_frontend.bat

echo.
echo ========================================
echo JARVIS is starting up!
echo ========================================
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo.
echo Press any key to exit this launcher...
pause >nul
