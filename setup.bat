@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
if errorlevel 1 (
  echo Setup failed. Check your network and try setup.bat again.
  pause
  exit /b 1
)
call "%~dp0run_app.bat"

