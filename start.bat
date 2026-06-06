@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo Telegram Message Manager - Starting
echo ============================================
echo.

if not exist venv (
    echo Virtual environment not found
    echo Please run install.bat first
    pause
    exit /b 1
)

if not exist .env (
    echo .env file not found
    echo Please run install.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

for /f "tokens=2 delims==" %%a in ('findstr "TELEGRAM_API_ID" .env') do set API_ID=%%a
for /f "tokens=2 delims==" %%a in ('findstr "TELEGRAM_API_HASH" .env') do set API_HASH=%%a

if "!API_ID!"=="" (
    echo.
    echo [WARNING] TELEGRAM_API_ID not configured in .env
    echo [WARNING] TELEGRAM_API_HASH not configured in .env
    echo.
    echo Please get your credentials from: https://my.telegram.org
    echo.
)

echo Starting Flask application...
echo.
echo Application will be available at: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

timeout /t 2 >nul

start http://127.0.0.1:5000

python app.py
