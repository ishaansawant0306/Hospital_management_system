@echo off
echo Starting Backend Jobs (Celery Worker + Beat)...

cd backend

REM Start Worker in a new window using Python
start "Celery Worker" cmd /k "python run_worker.py"

REM Start Beat in a new window using Python
start "Celery Beat" cmd /k "python run_beat.py"

echo.
echo Jobs started in background windows!
echo Keep this window open or close it, the jobs will run in the new windows.
echo.
pause
