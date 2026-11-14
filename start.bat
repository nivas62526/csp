@echo off
title Smart Poultry Farm - Precision Management System
echo ========================================================
echo    🐔 SMART POULTRY FARM - IOT & AI PLATFORM
echo ========================================================
echo.

set "PY_CMD=python"
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set "PY_CMD=py"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    )
)

echo [1/3] Initializing database and schemas...
"%PY_CMD%" database.py
echo.
echo [2/3] Opening Project Overview showcase in browser...
start "" http://localhost:5000/overview
echo.
echo [3/3] Starting Application Server on http://localhost:5000...
echo (Keep this command window open while testing the application)
echo.
"%PY_CMD%" app.py
pause
