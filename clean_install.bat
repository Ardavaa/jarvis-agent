@echo off
echo ========================================
echo Performing Clean Install for JARVIS (Robust Mode)
echo ========================================
echo.

echo 1. Stopping any running Python processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM uvicorn.exe >nul 2>&1

echo.
if exist .venv (
    echo 2. Removing corrupted .venv directory...
    rmdir /s /q .venv
    if exist .venv (
        echo    ERROR: Could not remove .venv. Files might be in use.
        echo    Please manually delete the '.venv' folder and run this script again.
        pause
        exit /b 1
    ) else (
        echo    .venv removed successfully.
    )
) else (
    echo    No .venv found, proceeding.
)

echo.
echo 3. Creating new virtual environment...
uv venv
if %ERRORLEVEL% NEQ 0 (
    echo    ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

echo.
echo 4. Installing dependencies (including websockets fix)...
uv sync
if %ERRORLEVEL% NEQ 0 (
    echo    ERROR: Dependency installation failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Clean install complete!
echo You can now run start_jarvis.bat
echo ========================================
echo.
pause
