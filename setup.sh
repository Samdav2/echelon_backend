#!/bin/bash

# FastAPI Ticket System Setup Script

echo "================================"
echo "FastAPI Ticket System Setup"
echo "================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "✓ Virtual environment created"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✓ Pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠ .env file created from .env.example"
    echo "⚠ Please update .env with your configuration"
else
    echo "✓ .env file already exists"
fi
echo ""

# Create uploads directory
mkdir -p uploads
echo "✓ Uploads directory created"
echo ""

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Ensure MySQL is running"
echo "3. Create database: mysql -u root -p -e 'CREATE DATABASE ticket_db;'"
echo "4. Run migrations (if applicable)"
echo "5. Start the server: python3 main.py"
echo ""
echo "Or use Uvicorn directly:"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 5000"
echo ""
