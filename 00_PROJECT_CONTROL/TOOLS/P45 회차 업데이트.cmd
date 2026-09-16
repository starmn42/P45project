@echo off
chcp 65001 >nul
for %%I in ("%~dp0..\..") do set "P45_ROOT=%%~fI"
cd /d "%P45_ROOT%"
set "PYTHONPATH=%CD%\src"
set "P45_PYTHON=C:\Users\sung2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
echo P45 공식 회차 업데이트
echo 동행복권 결과를 확인하고 별도 운영 저장소만 갱신합니다.
"%P45_PYTHON%" -m p45_v27.draw_update update
echo.
if /I not "%~1"=="scheduled" pause
