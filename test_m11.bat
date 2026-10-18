@echo off
setlocal
cd /d "%~dp0"
echo Starting Milestone 11 real-data verification...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0test_m11.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if "%EXIT_CODE%"=="0" (echo [RESULT] REAL-DATA FOUNDATION PASSED) else (echo [RESULT] REAL-DATA FOUNDATION FAILED with exit code %EXIT_CODE%)
echo.
pause
exit /b %EXIT_CODE%
