#!/bin/bash
# Linux equivalent of Run.bat for decklist_to_pdf
set -e

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed. Please install Python3."
    exit 1
fi

# Check if venv module is available
if ! python3 -m venv --help &> /dev/null; then
    echo "ERROR: The 'venv' module is not available. You may need a newer Python version (3.3+)."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Using existing virtual environment."
fi

# Create necessary folders
for d in scryfall_bulk_json cardbacks custom_cards image_cache output input; do
    if [ ! -d "$d" ]; then
        mkdir "$d"
        echo "Created: $d folder"
    fi
done

# Create subdirectories in image_cache
for sub in small normal large png art_crop border_crop; do
    if [ ! -d "image_cache/$sub" ]; then
        mkdir -p "image_cache/$sub"
        echo "Created: image_cache/$sub"
    fi
done

# Create the decklist file if it doesn't exist
if [ ! -f input/test_deck.txt ]; then
    cat << EOF > input/decklist.txt
1 Yahenni, Undying Partisan (CMM) 201
1 Accursed Marauder (MH3) 80
1 Animate Dead (MKC) 125
1 Blood Seeker (ZEN) 80
1 Carrier Thrall (2X2) 72
1 Cartouche of Ambition (AKH) 83
1 Creeping Bloodsucker (J22) 21
1 Crypt Rats (VIS) 55
1 Cult Conscript (DMU) 88
1 Dance of the Dead (ICE) 118
1 Deathgreeter (DDD) 33
1 Death's-Head Buzzard (VMA) 115
EOF
    echo "Created: decklist.txt"
else
    echo "decklist.txt already exists, not overwriting."
fi

# Activate the virtual environment and run the script
source .venv/bin/activate
echo "Installing required packages..."
pip install --upgrade pip
pip install reportlab Pillow requests orjson PyPDF2 img2pdf
echo "Setup complete, launching script."
python3 decklist_to_pdf.py
deactivate
