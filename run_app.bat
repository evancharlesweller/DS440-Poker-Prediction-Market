@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 main.py
    goto :eof
)

where python >nul 2>nul
if %errorlevel%==0 (
    python main.py
    goto :eof
)

echo Python was not found on this system.
echo Install Python 3 first, then run this file again.
pause
