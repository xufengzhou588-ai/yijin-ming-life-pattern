@echo off
cd /d "%~dp0"
title MING Life Pattern Server
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8787/?v=75"
echo Starting MING Life Pattern...
echo Keep this window open while using the website.
echo.
python server.py
if errorlevel 1 (
  echo.
  echo The server could not start. Check whether port 8787 is already in use.
  pause
)
