#!/bin/bash

# Quick Start Script for Photo Metadata Manipulator

echo "=========================================="
echo "Photo Metadata Manipulator - Quick Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip3 install -r requirements.txt

echo ""
echo "✓ Dependencies installed successfully!"
echo ""

# Run the application
echo "Starting Photo Metadata Manipulator..."
echo ""
cd src
python3 main.py
