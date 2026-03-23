@echo off
:: Check if already running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run
) else (
    :: Re-launch with UAC elevation
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%~dp0\" && python main.py && pause' -Verb RunAs"
    exit /b
)

:run
cd /d "%~dp0"
python main.py
if %errorLevel% neq 0 (
    echo.
    echo ERROR: App crashed. Check that Python is installed and customtkinter is available.
    echo Run: pip install customtkinter
    pause
)
