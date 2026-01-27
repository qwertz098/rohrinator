@echo off
REM Rohrinator - Windows Local Setup Script
REM This script clones the repository, sets up Python environment, and runs the server

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Rohrinator - Pipe Assembly Generator
echo ========================================
echo.

REM Configuration
set "REPO_URL=https://github.com/YOUR_USERNAME/rohrinator.git"
set "BRANCH=main"
set "PORT=8000"

REM Check for Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo       Found Python %PYVER%

REM Check for Git
echo [2/5] Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)
echo       Git found

REM Clone or update repository
echo [3/5] Setting up repository...
if exist "rohrinator" (
    echo       Repository exists, pulling latest changes...
    cd rohrinator
    git pull origin %BRANCH%
    cd ..
) else (
    echo       Cloning repository...
    git clone --branch %BRANCH% %REPO_URL% rohrinator
    if errorlevel 1 (
        echo ERROR: Failed to clone repository
        echo Make sure the REPO_URL is correct in this script
        pause
        exit /b 1
    )
)

cd rohrinator

REM Create virtual environment
echo [4/5] Setting up Python environment...
if not exist "venv" (
    echo       Creating virtual environment...
    python -m venv venv
)

REM Activate venv and install dependencies
echo       Installing dependencies (this may take a few minutes)...
call venv\Scripts\activate.bat

pip install --upgrade pip >nul 2>&1
pip install cadquery fastapi "uvicorn[standard]" pydantic >nul 2>&1

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Try running manually: pip install cadquery fastapi uvicorn pydantic
    pause
    exit /b 1
)

echo       Dependencies installed

REM Start the server
echo [5/5] Starting server...
echo.
echo ========================================
echo   Server starting on port %PORT%
echo ========================================
echo.
echo   Web UI:    http://localhost:%PORT%
echo   API Docs:  http://localhost:%PORT%/docs
echo.
echo   Press Ctrl+C to stop the server
echo ========================================
echo.

python -m uvicorn rohrinator.api.main:app --host 127.0.0.1 --port %PORT% --reload

pause
