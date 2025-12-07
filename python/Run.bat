@echo off
REM Run script for decklist_to_pdf

REM Check if Python is installed and in PATH
python -V >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH. Please install Python.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist .venv\ (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo Using existing virtual environment.
)

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing required packages...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

REM Run the script (directories are created automatically)
echo Launching decklist_to_pdf...
python main.py

call .venv\Scripts\deactivate.bat
pause
exit /b 0
