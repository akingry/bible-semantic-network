@echo off
title Bible Keywords Network
echo.
echo ========================================
echo   Bible Keywords Network Visualization
echo ========================================
echo.

cd /d "%~dp0"

:: Build network data if needed
if not exist "network_data.json" (
    echo Building network data...
    python build_network.py
    echo.
)

:: Start server
echo Starting visualization server...
python server.py

pause
