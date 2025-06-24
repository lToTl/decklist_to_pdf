@echo off
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

if not exist .venv\ (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo Using existing virtual environment.
)
echo Checking and creating necessary folders...

REM Check and create main directories
if not exist scryfall_bulk_json mkdir scryfall_bulk_json && echo Created: scryfall_bulk_json folder
if not exist cardbacks mkdir cardbacks && echo Created: cardbacks folder
if not exist custom_cards mkdir custom_cards && echo Created: custom_cards folder
if not exist image_cache mkdir image_cache && echo Created: image_cache folder
if not exist output mkdir output && echo Creatrd: output folder

REM Check and create subdirectories in image_cache
if not exist image_cache\small mkdir image_cache\small && echo Created: image_cache\small
if not exist image_cache\normal mkdir image_cache\normal && echo Created: image_cache\normal
if not exist image_cache\large mkdir image_cache\large && echo Created: image_cache\large
if not exist image_cache\png mkdir image_cache\png && echo Created: image_cache\png
if not exist image_cache\art_crop mkdir image_cache\art_crop && echo Created: image_cache\art_crop
if not exist image_cache\border_crop mkdir image_cache\border_crop && echo Created: image_cache\border_crop

REM Create the decklist file
if not exist decklist.txt (
    (
    echo 1 Yahenni, Undying Partisan ^(CMM^) 201
    echo 1 Accursed Marauder ^(MH3^) 80
    echo 1 Animate Dead ^(MKC^) 125
    echo 1 Blood Seeker ^(ZEN^) 80
    echo 1 Carrier Thrall ^(2X2^) 72
    echo 1 Cartouche of Ambition ^(AKH^) 83
    echo 1 Creeping Bloodsucker ^(J22^) 21
    echo 1 Crypt Rats ^(VIS^) 55
    echo 1 Cult Conscript ^(DMU^) 88
    echo 1 Dance of the Dead ^(ICE^) 118
    echo 1 Deathgreeter ^(DDD^) 33
    echo 1 Death's-Head Buzzard ^(VMA^) 115
    ) > decklist.txt
    echo Created: decklist.txt
) else (
    echo using existing decklist.txt
)

REM Activate the virtual environment and run the script
call .venv\Scripts\activate.bat
echo Installing required packages...
pip install reportlab Pillow requests orjson
echo Setup complete, launching script.
python decklist_to_pdf.py
call .venv\Scripts\deactivate.bat
pause
exit /b 0
