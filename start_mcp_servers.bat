@echo off
echo ========================================
echo Starting JARVIS MCP Servers
echo ========================================
echo.

echo Starting MCP Memory DB Server (Port 8001)...
start "MCP Memory DB" cmd /k "set PYTHONPATH=%cd% && cd mcp_servers\mcp-memory-db && uv run python server.py"
timeout /t 2 /nobreak >nul

echo Starting MCP Vector DB Server (Port 8002)...
start "MCP Vector DB" cmd /k "set PYTHONPATH=%cd% && cd mcp_servers\mcp-vector-db && uv run python server.py"
timeout /t 2 /nobreak >nul

echo Starting MCP Telegram Server (Port 8003)...
start "MCP Telegram" cmd /k "set PYTHONPATH=%cd% && cd mcp_servers\mcp-telegram && uv run python server.py"
timeout /t 2 /nobreak >nul

echo Starting MCP Google Calendar Server (Port 8004)...
start "MCP Calendar" cmd /k "set PYTHONPATH=%cd% && cd mcp_servers\mcp-calendar-google && uv run python server.py"
timeout /t 2 /nobreak >nul

echo Starting MCP Gmail Server (Port 8005)...
start "MCP Gmail" cmd /k "set PYTHONPATH=%cd% && cd mcp_servers\mcp-gmail && uv run python server.py"
timeout /t 2 /nobreak >nul

echo Starting MCP Windows OS Server (Port 8006)...
start "MCP Windows OS" cmd /k "set PYTHONPATH=%cd% && cd mcp_servers\mcp-windows-os && uv run python server.py"
timeout /t 2 /nobreak >nul

echo Starting MCP Voice Server (Port 8007)...
start "MCP Voice" cmd /k "set PYTHONPATH=%cd% && cd mcp_servers\mcp-voice && uv run python server.py"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo All MCP Servers Started!
echo ========================================
echo Memory DB:    http://localhost:8001
echo Vector DB:    http://localhost:8002
echo Telegram:     http://localhost:8003
echo Calendar:     http://localhost:8004
echo Gmail:        http://localhost:8005
echo Windows OS:   http://localhost:8006
echo Voice:        http://localhost:8007
echo ========================================
echo.
echo Press any key to exit...
pause >nul
