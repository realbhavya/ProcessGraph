@echo off
setlocal
cd /d "%~dp0"
echo Starting Milestone 12 OPC UA live-replay verification...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0test_m12.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if "%EXIT_CODE%"=="0" (echo [RESULT] OPC UA LIVE REPLAY PASSED) else (echo [RESULT] OPC UA LIVE REPLAY FAILED with exit code %EXIT_CODE%)
echo.
pause
exit /b %EXIT_CODE%
