@echo off
setlocal enabledelayedexpansion
set PATH=C:\Program Files\nodejs;%PATH%
cd /d "d:\IITM\MAD_2\MAD_2-main\MAD_2-main\Hospital_management_system\frontend-clean"
echo Starting build...
call npm run build
echo Build finished!
pause
