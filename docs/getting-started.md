# Getting Started

This guide will help you get Decklist to PDF up and running on your system.

## 📋 Prerequisites

Choose your preferred implementation:

| Implementation | Requirements |
|---------------|--------------|
| Python Script | Python 3.10+ |
| Dart CLI | Dart SDK 2.17+ |
| Flutter App | Flutter SDK 3.9+ |

## 🐍 Python Script (Recommended for Beginners)

### Automatic Setup

The easiest way to get started is using the provided scripts:

**Linux/macOS:**
```bash
chmod +x Run.sh
./Run.sh
```

**Windows:**
```cmd
Run.bat
```

These scripts will:
1. Check Python installation
2. Create a virtual environment
3. Create necessary directories
4. Install required packages
5. Create a sample decklist
6. Run the script

### Manual Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install Pillow requests orjson PyPDF2 img2pdf

# Create directories
mkdir -p scryfall_bulk_json cardbacks custom_cards output input
mkdir -p image_cache/{small,normal,large,png,art_crop,border_crop}

# Run the script
python decklist_to_pdf.py
```

## 🎯 Dart CLI

### Setup

```bash
# Install dependencies
dart pub get

# Run the script
dart run decklist_to_pdf.dart
```

### Command-Line Arguments

```bash
dart decklist_to_pdf.dart [OPTIONS]

Options:
  -h, --help              Show help message
  -i, --input NAME        Decklist file name (without .txt)
  -o, --output NAME       Output PDF name (without .pdf)
  -t, --two-sided BOOL    Enable two-sided printing
  -d, --dpi INT           DPI for rendering (default: 300)
  -w, --worker-threads N  Number of download threads
```

## 📱 Flutter App

### Setup

```bash
cd flutter_app_d2pdf

# Install dependencies
flutter pub get

# Generate Hive adapters
dart run build_runner build

# Run the app
flutter run
```

### Supported Platforms

- ✅ Windows
- ✅ macOS  
- ✅ Linux
- ✅ Android
- ✅ iOS
- ✅ Web

## 🃏 Your First PDF

### Step 1: Create a Decklist

Create a file `input/my_deck.txt`:

```
# My First Deck
# Lines starting with # are comments

1 Lightning Bolt (2X2) 117
4 Counterspell (CMM) 81
2 Sol Ring (CMM) 421
1 Black Lotus (VMA) 4
```

### Step 2: Run the Script

**Python:**
```bash
python decklist_to_pdf.py
# Enter: my_deck
```

**Dart:**
```bash
dart decklist_to_pdf.dart -i my_deck
```

### Step 3: Find Your PDF

The generated PDF will be at:
```
output/my_deck.pdf
```

## ⚙️ First-Run Configuration

On first run, the script will:

1. **Download Scryfall Data**: Prompts to download/update the bulk JSON (~500MB)
2. **Create Configuration**: Generates `decklist_to_pdf.ini` with defaults
3. **Create Directories**: Sets up the folder structure

You'll be asked:
```
Do you want to update Scryfall bulk JSON? (y/n):
```

Answer `y` on first run to download the card database.

## 📁 Directory Structure After Setup

```
decklist_to_pdf/
├── decklist_to_pdf.ini        # Your configuration
├── input/
│   └── my_deck.txt            # Your decklists
├── output/
│   └── my_deck.pdf            # Generated PDFs
├── image_cache/
│   └── png/                   # Cached card images
├── scryfall_bulk_json/
│   └── default-cards-*.json   # Card database
├── custom_cards/              # Your custom card images
└── cardbacks/                 # Custom back images
```

## 🔄 Updating Scryfall Data

To update the card database (new sets, errata, etc.):

```bash
python decklist_to_pdf.py
# Answer 'y' when prompted about updating Scryfall bulk JSON
```

Or manually delete the cached file:
```bash
rm scryfall_bulk_json/*.json
```

## ⏭️ Next Steps

- [Configuration Guide](configuration.md) - Customize print settings
- [Decklist Format](decklist-format.md) - Advanced decklist syntax
- [Troubleshooting](troubleshooting.md) - Common issues

---

[← Back to Home](README.md)
