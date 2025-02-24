@echo off
echo Setting up virtual environment...

REM Check if Python is installed and in PATH
python -V >nul 2>&1
if %ERRORLEVEL% == 1 (
    echo "ERROR: Python is not installed or not in PATH. Please install Python."
    pause
    exit /b 1
)

REM Check if venv module is available (Python 3.3+)
python -m venv --help >nul 2>&1
if %ERRORLEVEL% == 1 (
    echo "ERROR: The 'venv' module is not available.  You may need a newer Python version (3.3+)."
    pause
    exit /b 1
)

REM Create the virtual environment named '.venv'
python -m venv .venv
echo created venv
REM Activate the virtual environment
call .venv\Scripts\activate.bat
echo activated venv
echo Installing required packages...

REM Install packages from requirements.txt
pip install -r requirements.txt

echo python decklist_to_pdf.py>RUN.bat

echo Setup complete.

start RUN.bat

del requirements.txt
del "%~f0"

pause
exit /b 0