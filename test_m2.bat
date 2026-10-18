@echo off
setlocal
cd /d "%~dp0"
echo Starting Milestone 3 verification with Windows PowerShell...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0test_m3.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if "%EXIT_CODE%"=="0" (
  echo [RESULT] ALL TESTS PASSED
) else (
  echo [RESULT] TESTS FAILED with exit code %EXIT_CODE%
)
echo.
pause
exit /b %EXIT_CODE%
