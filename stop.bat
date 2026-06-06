@echo off
echo.
echo Stopping Telegram Message Manager...
echo.

taskkill /f /im python.exe >nul 2>&1

if errorlevel 0 (
    echo [OK] Application stopped
) else (
    echo [INFO] No running instance found
)

echo.
pause
