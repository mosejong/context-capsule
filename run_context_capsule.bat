@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_dashboard.ps1"
if errorlevel 1 (
  echo.
  echo Context Capsule failed to start.
  pause
)
