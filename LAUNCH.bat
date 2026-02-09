@echo off
title xsvCommandCenter [GHOST SHELL]
color 0a
cls

:: Set Path to current folder so Python can find src/
set "PYTHONPATH=%~dp0"

echo [*] Initializing Core...
echo [*] Loading Modules...
echo.

:: Run the Shell Command
python "%~dp0src\main.py" shell

:: If it crashes, keep window open to see error
if %errorlevel% neq 0 pause