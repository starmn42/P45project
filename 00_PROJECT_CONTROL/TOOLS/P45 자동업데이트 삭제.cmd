@echo off
chcp 65001 >nul
echo P45 자동 회차 업데이트 예약만 삭제합니다.
schtasks.exe /Delete /TN "P45 Weekly Draw Update" /F
if errorlevel 1 (
  echo.
  echo 예약이 없거나 삭제하지 못했습니다.
) else (
  echo.
  echo P45 예약 작업을 삭제했습니다.
)
pause
