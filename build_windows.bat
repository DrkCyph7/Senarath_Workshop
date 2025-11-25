@echo off
REM Batch script to build Windows EXE for Senarath Workshop System

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Senarath Workshop - Windows Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.13+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo [1/5] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo [3/5] Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Ensure ui/db directory exists
echo [4/5] Ensuring database directory exists...
if not exist "ui\db" (
    mkdir ui\db
    echo Created ui\db directory
)

REM Build executable
echo [5/5] Building executable...
pyinstaller --clean build_exe.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Build Complete
echo ========================================
echo.
echo Your executable is ready at:
echo   dist\SenarathWorkshop.exe
echo.
echo This can be run on any Windows machine without Python!
echo.
pause
