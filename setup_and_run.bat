@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=py -3"
    goto have_python
)

where python >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=python"
    goto have_python
)

echo Python was not found on this system.
echo Please install Python 3 and make sure it is available on PATH.
pause
goto :eof

:have_python
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PY_CMD% -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        goto :eof
    )
)

echo Installing dependencies...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    goto :eof
)

echo Launching Poker Prediction Market...
python main.py
