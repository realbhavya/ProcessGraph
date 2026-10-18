@echo off
setlocal
cd /d "%~dp0"
echo Starting Milestone 10 release verification with Windows PowerShell...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0test_m10.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if "%EXIT_CODE%"=="0" (echo [RESULT] RELEASE GATE PASSED) else (echo [RESULT] RELEASE GATE FAILED with exit code %EXIT_CODE%)
echo.
pause
exit /b %EXIT_CODE%
