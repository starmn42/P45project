@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo P45 자동 회차 업데이트 예약을 등록합니다.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0P45 자동업데이트 설치.ps1"
if errorlevel 1 (
  echo.
  echo 등록에 실패했습니다. 오류 내용을 확인하세요.
) else (
  echo.
  echo 등록이 완료되었습니다.
)
pause
