@echo off
setlocal
cd /d "%~dp0"
title Transcription

if not exist input mkdir input
if not exist output mkdir output

rem ---- 1. Find Python (install it automatically if missing) ----
set "PY="
python -c "import sys" >nul 2>&1 && set "PY=python"
if not defined PY (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)
if not defined PY (
    echo Python was not found. Installing it now, this takes a few minutes...
    winget install --id Python.Python.3.12 -e --scope user --accept-package-agreements --accept-source-agreements
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)
if not defined PY (
    echo.
    echo Could not install Python automatically.
    echo Please install it from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^)
    echo and then double-click run.bat again.
    goto :end
)

rem ---- 2. First-time setup: private environment + libraries ----
if not exist .venv\Scripts\python.exe (
    echo Setting up for the first time, please wait...
    "%PY%" -m venv .venv || goto :err
)
if not exist .venv\.installed (
    .venv\Scripts\python -m pip install -r requirements.txt || goto :err
    echo done> .venv\.installed
)

rem ---- 3. Transcribe everything in the input folder ----
echo.
echo Transcribing files from the "input" folder. The first run also downloads the
echo speech model ^(about 1.6 GB^), so it needs an internet connection.
echo.
.venv\Scripts\python transcribe.py %*
echo.
echo Finished. Results are in the "output" folder.
goto :end

:err
echo.
echo Setup failed. Check your internet connection and try again.
rmdir /s /q .venv 2>nul

:end
echo.
pause
