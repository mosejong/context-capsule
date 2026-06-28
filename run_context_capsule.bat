@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_dashboard.ps1"
if errorlevel 1 (
  echo.
  echo Context Capsule 실행에 실패했습니다.
  echo 자세한 내용은 outputs\logs 폴더의 최신 로그를 확인하세요.
  echo START_HERE_KO.md 또는 docs\local_app.md를 참고하세요.
  pause
)
