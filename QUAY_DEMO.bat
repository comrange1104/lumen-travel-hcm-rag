@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Please install the Python environment using README.md first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" scripts\start_recording.py
pause
