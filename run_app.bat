@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
  start "" ".venv\Scripts\pythonw.exe" "%~dp0launcher.py"
  exit /b
)
if exist ".runtime\tools\pythonw.exe" (
  start "" ".runtime\tools\pythonw.exe" "%~dp0launcher.py"
  exit /b
)
echo First run: preparing this app on your computer...
call "%~dp0setup.bat"

