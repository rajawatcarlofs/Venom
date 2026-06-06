@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo Telegram Message Manager - Installation
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.12+ from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python found
echo.

echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

echo.
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

echo.
echo Creating required directories...
if not exist sessions mkdir sessions
if not exist logs mkdir logs
if not exist uploads mkdir uploads
echo [OK] Directories created

if not exist .env (
    echo.
    echo Creating .env file...
    copy .env.example .env >nul
    echo [OK] .env file created - Please edit with your Telegram API credentials
)

echo.
echo Initializing database...
python -c "from database import init_db; init_db(); print('[OK] Database initialized')"
if errorlevel 1 (
    echo Error: Failed to initialize database
    pause
    exit /b 1
)

echo.
echo ============================================
echo Installation completed successfully!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file with your Telegram API credentials
echo 2. Run start.bat to launch the application
echo.
pause
