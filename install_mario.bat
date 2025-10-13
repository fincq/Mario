@echo off
title Mario Setup
echo ================================
echo        Mario Setup
echo ================================
echo.
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Install Python from https://python.org
    echo Check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo Python found
echo.
echo Installing Mario...
pip install --editable .
if %errorlevel% neq 0 (
    echo Installation failed
    echo Trying with python -m pip...
    python -m pip install --editable .
    if %errorlevel% neq 0 (
        echo Installation failed. Check your Python setup.
        pause
        exit /b 1
    )
)
echo.
echo ================================
echo   Installation Complete
echo ================================
echo.
echo Run Mario with:
echo   python -m mario
echo.
echo Press any key to start Mario now...
pause >nul
echo.
python -m mario
pause