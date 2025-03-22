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

if exist scryfall_bulk_json ( 
	call .venv\Scripts\activate.bat
	python decklist_to_pdf.py
	pause
	exit /b 0
	)
ELSE (
	mkdir scryfall_bulk_json
	mkdir cardbacks
	mkdir image_cache
	cd image_cache
	mkdir small
	mkdir normal
	mkdir large
	mkdir png
	mkdir art_crop
	mkdir border_crop
	cd ..
	echo 1 Yahenni, Undying Partisan (CMM) 201>>decklist.txt
	echo 1 Accursed Marauder (MH3) 80>>decklist.txt
	echo 1 Animate Dead (MKC) 125>>decklist.txt
	echo 1 Blood Seeker (ZEN) 80>>decklist.txt
	echo 1 Carrier Thrall (2X2) 72>>decklist.txt
	echo 1 Cartouche of Ambition (AKH) 83>>decklist.txt
	echo 1 Creeping Bloodsucker (J22) 21>>decklist.txt
	echo 1 Crypt Rats (VIS) 55>>decklist.txt
	echo 1 Cult Conscript (DMU) 88>>decklist.txt
	echo 1 Dance of the Dead (ICE) 118>>decklist.txt
	echo 1 Deathgreeter (DDD) 33>>decklist.txt
	echo 1 Death's-Head Buzzard (VMA) 115>>decklist.txt
	echo created directories and decklist.txt
	REM Activate the virtual environment
	call .venv\Scripts\activate.bat
	echo activated venv
	echo Installing required packages...

	REM Install packages
	pip install reportlab Pillow requests

	echo Setup complete, launching script.
	python decklist_to_pdf.py
	)

pause
exit /b 0