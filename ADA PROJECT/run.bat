@echo off
title Cloud Computing Job Scheduler
cd /d "%~dp0"

echo ======================================================================
echo    Cloud Computing Job Scheduler (Greedy with DSU and Deadlines)
echo ======================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH!
    echo Please install Python 3.8+ and ensure it is added to your PATH.
    pause
    exit /b 1
)

echo Checking dependencies...
python -m pip install -r requirements.txt --quiet

echo.
echo Launching Application Menu...
python main.py

pause
