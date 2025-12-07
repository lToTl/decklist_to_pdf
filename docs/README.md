# Decklist to PDF - Documentation

Welcome to the **Decklist to PDF** documentation wiki! This project helps Magic: The Gathering players generate printable PDF files from decklists.

## 📖 Overview

Decklist to PDF is a tool that:
- Loads Scryfall bulk JSON card data
- Reads decklist files in a specific format
- Downloads and caches card images from Scryfall
- Renders 9-card pages to A4 PDF format for printing
- Supports various print customization options

## 🚀 Quick Links

| Documentation | Description |
|--------------|-------------|
| [Getting Started](getting-started.md) | Installation and first-time setup |
| [Configuration](configuration.md) | All configuration options explained |
| [Decklist Format](decklist-format.md) | How to write decklist files |
| [Architecture](architecture.md) | Project structure and design |

## 📦 Implementations

This project provides three implementations:

| Implementation | Description | Documentation |
|---------------|-------------|---------------|
| **Python Script** | Original command-line tool | [Python Script](python-script.md) |
| **Dart CLI** | Dart port for command-line use | [Dart CLI](dart-cli.md) |
| **Flutter App** | Cross-platform GUI application | [Flutter App](flutter-app.md) |

## 🔧 Reference

| Documentation | Description |
|--------------|-------------|
| [API Reference](api-reference.md) | Function and class documentation |
| [Troubleshooting](troubleshooting.md) | Common issues and solutions |

## ✨ Features

### Core Features
- **Scryfall Integration**: Automatically downloads and parses Scryfall bulk data
- **Image Caching**: Downloads card images once, reuses from cache
- **High-Quality Output**: Configurable DPI (up to 600) for professional prints
- **A4 Page Layout**: Standard 3x3 grid of cards per page

### Print Options
- **Two-Sided Printing**: Organizes pages for front/back printing
- **Staggered Output**: Optimizes page order for slow printers
- **Reference Points**: CNC locator marks for cutting alignment
- **Adjustable Spacing**: Configurable gaps between cards
- **X-Axis Offset**: Compensate for printer margins

### Card Support
- **Standard Cards**: Normal, token, split, adventure, saga, etc.
- **Two-Sided Cards**: Transform, modal DFC, reversible cards
- **Custom Cards**: Local image files for proxies
- **Composite Cards**: Mix different fronts and backs
- **Gamma Correction**: Adjusts image contrast for better prints

## 📂 Project Structure

```
decklist_to_pdf/
├── decklist_to_pdf.py      # Python implementation
├── decklist_to_pdf.dart    # Dart CLI implementation
├── Run.sh / Run.bat        # Setup and run scripts
├── pubspec.yaml            # Dart dependencies
├── decklist_to_pdf.ini     # Configuration file
├── flutter_app_d2pdf/      # Flutter GUI application
│   ├── lib/
│   │   ├── main.dart              # App entry point and UI
│   │   ├── decklist_to_pdf.dart   # Core logic (Dart)
│   │   ├── card_data_model.dart   # Data models
│   │   └── data_service.dart      # Hive data service
│   └── ...
├── docs/                   # This documentation
├── input/                  # Decklist files go here
├── output/                 # Generated PDFs
├── image_cache/            # Downloaded card images
├── custom_cards/           # Custom card images
├── cardbacks/              # Custom back images
└── scryfall_bulk_json/     # Scryfall data cache
```

## 📋 Requirements

### Python Script
- Python 3.10+
- Dependencies: `Pillow`, `requests`, `orjson`, `PyPDF2`, `img2pdf`

### Dart CLI
- Dart SDK 2.17+
- Dependencies: `http`, `image`, `pdf`, `path`

### Flutter App
- Flutter SDK 3.9+
- Additional dependencies: `provider`, `file_picker`, `hive`, `printing`

## 📝 License

MIT License - See [LICENSE](../LICENSE) for details.

---

*Last updated: December 2025*
