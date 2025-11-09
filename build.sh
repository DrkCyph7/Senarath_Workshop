#!/bin/bash

# Shell script to build executable for Senarath Workshop System
# Works on macOS and Linux

set -e

echo ""
echo "========================================"
echo "Senarath Workshop - Build Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.13+ first"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "[2/4] Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "[3/4] Installing dependencies..."
pip install -q -r requirements.txt

# Build executable
echo "[4/4] Building executable..."
pyinstaller --clean build_exe.spec

echo ""
echo "========================================"
echo "SUCCESS! Build Complete"
echo "========================================"
echo ""
echo "Your executable is ready at:"
echo "  ./dist/SenarathWorkshop"
echo ""
echo "To run it:"
echo "  ./dist/SenarathWorkshop"
echo ""
