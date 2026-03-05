@echo off
setlocal enabledelayedexpansion

REM sol_summary one-click runner (Windows)
REM - create .venv if missing
REM - install requirements
REM - run API service on 0.0.0.0:8787

cd /d %~dp0

if not exist .venv (
  echo [INFO] Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Failed to create venv. Ensure Python 3 is installed.
    exit /b 1
  )
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
  echo [ERROR] Failed to activate venv.
  exit /b 1
)

echo [INFO] Installing/updating dependencies...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Dependency installation failed.
  exit /b 1
)

echo [INFO] Starting sol_summary API at http://0.0.0.0:8787 ...
set PYTHONPATH=src
python -m uvicorn sol_summary.api:app --host 0.0.0.0 --port 8787

endlocal
