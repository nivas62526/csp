@echo off
title Smart Poultry Farm Management System
echo ============================================================
echo   SMART POULTRY FARM MANAGEMENT SYSTEM
echo ============================================================
echo [1/3] Initializing Database & Verifying Tables...
"C:\Users\DELL\AppData\Local\Programs\Python\Python311\python.exe" init_db.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Database initialization failed.
    pause
    exit /b %ERRORLEVEL%
)

echo [2/3] Starting Flask Application on http://127.0.0.1:5000 ...
start "" "http://127.0.0.1:5000"

echo [3/3] Application Running! Press Ctrl+C to stop.
echo ============================================================
"C:\Users\DELL\AppData\Local\Programs\Python\Python311\python.exe" app.py
pause
