@echo off
REM Double-click this file to start Lead Finder on Windows. No typing needed.
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
  set PY=python
) else (
  where python3 >nul 2>nul
  if %errorlevel%==0 (set PY=python3) else (
    echo Python isn't installed. Get it free from https://www.python.org/downloads/
    echo IMPORTANT: on the installer's first screen, tick "Add python.exe to PATH".
    pause
    exit /b 1
  )
)

%PY% -c "import flask" >nul 2>nul
if errorlevel 1 (
  echo Installing Flask, one moment...
  %PY% -m pip install flask --quiet
)

echo.
echo Dashboard: http://127.0.0.1:5000
echo Leave this window open while you use it.
echo.
start "" http://127.0.0.1:5000
%PY% app.py
pause
