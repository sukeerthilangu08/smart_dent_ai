#!/bin/bash
# Quick Start Script for Smart Dent AI

echo "=========================================="
echo "Smart Dent AI - Quick Start"
echo "=========================================="
echo ""

# Check Python version
echo "1. Checking Python version..."
python3 --version

# Install dependencies
echo ""
echo "2. Installing dependencies..."
pip3 install -r requirements.txt

# Test the system
echo ""
echo "3. Testing analysis system..."
python3 test_analysis.py

# Start the server
echo ""
echo "4. Starting Flask server..."
echo ""
echo "✓ Server will start on http://localhost:8000"
echo "✓ Open your browser and navigate to: http://localhost:8000"
echo "✓ Press Ctrl+C to stop the server"
echo ""
echo "=========================================="
echo ""

cd backend
python3 app.py
