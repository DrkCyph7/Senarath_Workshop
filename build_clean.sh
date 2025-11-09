#!/bin/bash
# Senarath WMS Build Script - Clean Build Without Database

echo "🔨 Starting Senarath WMS Build Process..."
echo "=========================================="

# Ensure database doesn't exist
if [ -f "ui/db/senarath.db" ]; then
    echo "🗑️  Removing existing database..."
    rm -f ui/db/senarath.db
fi

# Clean previous build artifacts
if [ -d "build" ]; then
    echo "🧹 Cleaning previous build artifacts..."
    rm -rf build
fi

if [ -d "dist" ]; then
    echo "🧹 Cleaning previous dist folder..."
    rm -rf dist
fi

# Ensure virtual environment is activated
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found! Please run: python3 -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q PySide6==6.10.0 PySide6-Addons==6.10.0 PySide6-Essentials==6.10.0 shiboken6==6.10.0 pyinstaller==6.10.0

# Build executable
echo "🔨 Building executable..."
pyinstaller --onefile \
    --windowed \
    --name "Senarath WMS" \
    --icon="" \
    --add-data "ui/theme.py:ui" \
    --add-data "assets:assets" \
    --hidden-import=PySide6 \
    main.py

# Check if build was successful
if [ -f "dist/Senarath WMS" ] || [ -f "dist/Senarath WMS.exe" ]; then
    echo ""
    echo "✨ Build Successful! ✨"
    echo "=========================================="
    echo "📦 Executable location:"
    
    if [ -f "dist/Senarath WMS" ]; then
        echo "   dist/Senarath WMS (macOS)"
        ls -lh "dist/Senarath WMS"
    elif [ -f "dist/Senarath WMS.exe" ]; then
        echo "   dist/Senarath WMS.exe (Windows)"
        ls -lh "dist/Senarath WMS.exe"
    fi
    
    echo ""
    echo "✅ Executable is ready for distribution"
    echo "✅ Database will be created on first run"
    echo "=========================================="
else
    echo ""
    echo "❌ Build failed! Check output above for errors."
    exit 1
fi
