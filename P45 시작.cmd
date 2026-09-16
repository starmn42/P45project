@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "PYTHONPATH=%CD%\src"
set "P45_PYTHON=C:\Users\sung2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if not exist "%P45_PYTHON%" (
  echo [P45] Python runtime not found:
  echo %P45_PYTHON%
  pause
  exit /b 1
)

echo ==========================================
echo P45 PC START
echo ==========================================
echo ROOT: %CD%
echo PYTHONPATH: %PYTHONPATH%
echo URL: http://127.0.0.1:8045/
echo.

start "P45 WEB SERVER" cmd /k ""%P45_PYTHON%" -m p45_v27.webapp --host 127.0.0.1 --port 8045"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8045/"

exit /b 0
