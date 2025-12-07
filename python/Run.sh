#!/bin/bash
# Run script for decklist_to_pdf
set -e

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed. Please install Python3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Using existing virtual environment."
fi

# Activate the virtual environment
source .venv/bin/activate

# Install/upgrade dependencies
echo "Installing required packages..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Run the script (directories are created automatically)
echo "Launching decklist_to_pdf..."
python3 main.py

deactivate
