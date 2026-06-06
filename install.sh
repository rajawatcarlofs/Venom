#!/bin/bash

echo ""
echo "==========================================="
echo "Telegram Message Manager - Installation"
echo "==========================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.12+ first"
    exit 1
fi

echo "[OK] Python found: $(python3 --version)"
echo ""

echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    echo "[OK] Virtual environment created"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip > /dev/null 2>&1

echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi
echo "[OK] Dependencies installed"

echo ""
echo "Creating required directories..."
mkdir -p sessions
mkdir -p logs
mkdir -p uploads
echo "[OK] Directories created"

if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "[OK] .env file created - Please edit with your Telegram API credentials"
fi

echo ""
echo "Initializing database..."
python -c "from database import init_db; init_db(); print('[OK] Database initialized')"
if [ $? -ne 0 ]; then
    echo "Error: Failed to initialize database"
    exit 1
fi

echo ""
echo "==========================================="
echo "Installation completed successfully!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Telegram API credentials"
echo "2. Run ./start.sh to launch the application"
echo ""
