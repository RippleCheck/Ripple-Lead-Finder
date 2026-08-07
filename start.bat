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
echo Launching... your browser will open on its own.
echo The exact address is printed below.
echo.
REM app.py picks a free port and opens the browser itself, so nothing is
REM hardcoded here - that used to open the wrong address when 5000 was busy.
%PY% app.py
pause
