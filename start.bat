@echo off
REM Rohrinator - Quick Start (run from extracted folder)
REM Just double-click this file after extracting the repository

setlocal

echo.
echo ========================================
echo   Rohrinator - Pipe Assembly Generator
echo ========================================
echo.

set "PORT=8000"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.10+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Create venv if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate and install
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -q --upgrade pip
pip install -q cadquery fastapi "uvicorn[standard]" pydantic

echo.
echo ========================================
echo   Starting Rohrinator
echo ========================================
echo.
echo   Open in browser: http://localhost:%PORT%
echo.
echo   Press Ctrl+C to stop
echo ========================================
echo.

start "" "http://localhost:%PORT%"
python -m uvicorn rohrinator.api.main:app --host 127.0.0.1 --port %PORT%

pause
