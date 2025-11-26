@echo off
REM Development Mode - Starts both Vue dev server and Flask backend
REM Run this from the repository root

echo ========================================
echo Hospital Management System - Dev Mode
echo ========================================
echo.
echo This will start TWO servers:
echo   - Vue Dev Server (http://localhost:8080)
echo   - Flask Backend (http://localhost:5000)
echo.
echo You'll need to keep this window open.
echo Press Ctrl+C to stop both servers.
echo ========================================
echo.

REM Start Flask backend in a new window
start "Flask Backend" cmd /k "cd backend && python main.py"

REM Wait a moment for Flask to start
timeout /t 3 /nobreak > nul

REM Start Vue dev server in current window
echo Starting Vue dev server...
cd frontend-clean
npm run serve
