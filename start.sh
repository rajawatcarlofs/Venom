#!/bin/bash

echo ""
echo "==========================================="
echo "Telegram Message Manager - Starting"
echo "==========================================="
echo ""

if [ ! -d "venv" ]; then
    echo "Virtual environment not found"
    echo "Please run install.sh first"
    exit 1
fi

source venv/bin/activate

if [ ! -f ".env" ]; then
    echo ".env file not found"
    echo "Please run install.sh first"
    exit 1
fi

API_ID=$(grep "^TELEGRAM_API_ID" .env | cut -d '=' -f 2)
API_HASH=$(grep "^TELEGRAM_API_HASH" .env | cut -d '=' -f 2)

if [ -z "$API_ID" ] || [ "$API_ID" = "your_api_id" ]; then
    echo ""
    echo "[WARNING] TELEGRAM_API_ID not configured in .env"
    echo "[WARNING] Please get your credentials from: https://my.telegram.org"
    echo ""
fi

echo "Starting Flask application..."
echo ""
echo "Application will be available at: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop the server"
echo ""

sleep 2

if command -v xdg-open &> /dev/null; then
    xdg-open http://127.0.0.1:5000
elif command -v open &> /dev/null; then
    open http://127.0.0.1:5000
fi

python app.py
