@echo off
cd /d "%~dp0"
python teacher_app.py
if errorlevel 1 (
  echo.
  echo Start fehlgeschlagen. Hinweise oben beachten.
  pause
)
