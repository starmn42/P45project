@echo off
chcp 65001 >nul
for %%I in ("%~dp0..\..") do set "P45_ROOT=%%~fI"
cd /d "%P45_ROOT%"
set "PYTHONPATH=%P45_ROOT%\src"
set "P45_PYTHON=C:\Users\sung2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
"%P45_PYTHON%" -m p45_experiments.prospective_raw_capture capture
