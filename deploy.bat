@echo off
REM Quick Deploy Script - Builds frontend and copies to backend
REM Run this from the repository root

echo ========================================
echo Hospital Management System - Quick Deploy
echo ========================================
echo.

echo [1/3] Building frontend...
cd frontend-clean
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Frontend build failed!
    pause
    exit /b 1
)
cd ..

echo.
echo [2/3] Copying build files to backend...
powershell -ExecutionPolicy Bypass -File "backend\copy_dist_to_backend.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Copy failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Starting Flask server...
echo.
echo ========================================
echo Ready! Server will start on http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd backend
python main.py
