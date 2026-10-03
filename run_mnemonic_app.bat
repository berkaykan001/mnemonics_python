@echo off
cd /d "%~dp0"
py -3.13 main.py
if %errorlevel% neq 0 (
    echo.
    echo An error occurred. Press any key to exit...
    pause > nul
)
