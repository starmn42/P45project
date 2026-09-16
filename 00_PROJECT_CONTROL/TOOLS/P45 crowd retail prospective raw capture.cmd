@echo off
setlocal
for %%I in ("%~dp0..\..") do set "P45_ROOT=%%~fI"
cd /d "%P45_ROOT%"
set "PYTHONPATH=%P45_ROOT%\src"
"C:\Users\sung2\AppData\Local\Python\bin\python.exe" -m p45_experiments.crowd_retail_prospective_raw_capture capture
endlocal
