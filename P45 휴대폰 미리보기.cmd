@echo off
chcp 65001 >nul
cd /d "%~dp0"
title P45 MOBILE PREVIEW

set "PYTHONPATH=%CD%\src"
set "P45_PYTHON=C:\Users\sung2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if not exist "%P45_PYTHON%" (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python을 찾을 수 없습니다.
    pause
    exit /b 1
  )
  set "P45_PYTHON=python"
)

netstat -ano | findstr /R /C:":8045 .*LISTENING" >nul
if not errorlevel 1 (
  echo.
  echo [P45] 8045 포트가 이미 사용 중입니다.
  echo 기존 P45 웹 창을 닫은 뒤 다시 실행하세요.
  echo.
  pause
  exit /b 2
)

for /f "delims=" %%I in ('^"^"%P45_PYTHON%" -m p45_v27.lan_ip^"') do set "P45_LAN_IP=%%I"

if not defined P45_LAN_IP (
  echo 현재 PC의 LAN IPv4를 확인하지 못했습니다.
  echo Wi-Fi 연결을 확인한 뒤 다시 실행하세요.
  pause
  exit /b 3
)

echo ==================================================
echo                 P45 MOBILE PREVIEW
echo ==================================================
echo.
echo PC:
echo http://127.0.0.1:8045/
echo.
echo PHONE:
echo http://%P45_LAN_IP%:8045/
echo.
echo PC와 휴대폰이 같은 Wi-Fi에 연결되어 있어야 합니다.
echo 이 창을 닫으면 휴대폰 미리보기도 종료됩니다.
echo 인터넷에는 공개되지 않습니다.
echo.

start "" "http://127.0.0.1:8045/"
"%P45_PYTHON%" -m p45_v27.webapp --host 0.0.0.0 --port 8045

echo.
echo P45 MOBILE PREVIEW가 종료되었습니다.
pause
