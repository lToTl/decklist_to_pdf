# CardMonger (flutter_app_d2pdf)

A Flutter-based application for generating high-quality PDFs from card game decklists, specifically tailored for Magic: The Gathering proxies via the Scryfall API.

## Project Overview

- **Purpose**: Converts text-based decklists into printable A4 PDF pages with 9 cards per page.
- **Key Features**:
  - Scryfall API integration for card metadata and high-resolution images.
  - Support for double-sided cards and custom card backs.
  - Configurable printing options: gamma correction, staggering, bleed edges, and custom DPI.
  - Multi-threaded image fetching and processing.
  - Local caching of images and Scryfall bulk data.

## Technical Stack

- **Framework**: Flutter (Dart)
- **State Management**: Provider
- **Local Storage**: Hive (intended), File system for caching.
- **PDF Generation**: `pdf` and `printing` packages.
- **Image Processing**: `image` package.
- **API**: Scryfall Bulk Data.

## Project Structure

- `lib/main.dart`: Entry point and UI (DeckBuilder, PrintingPage).
- `lib/decklist_to_pdf.dart`: Core logic for configuration, image fetching, and PDF rendering.
- `lib/data_service.dart`: Handles Scryfall data indexing and retrieval.
- `input/`: Default directory for decklist text files.
- `output/`: Default directory for generated PDFs.
- `image_cache/`: Caching directory for downloaded card images.
- `scryfall_bulk_json/`: Storage for Scryfall's default-cards JSON data.

## AI Assistant Instructions

When assisting with this project, please keep the following in mind:

1.  **Core Logic**: Significant logic resides in `DecklistToPdfCore` within `lib/decklist_to_pdf.dart`. This class was originally translated from Python and retains some of its structure.
2.  **Configuration**: Settings are managed via a `Map<String, dynamic>` in the core class and persisted in `decklist_to_pdf.conf`.
3.  **Performance**: Image processing (especially gamma correction) can be resource-intensive. Be mindful of performance when suggesting UI or logic changes.
4.  **UI/UX**: The app uses a clean, cyan-themed Material Design. Tabs separate the "Deck Builder" (in progress) and "Printing" functionalities.
5.  **Dependencies**: Always check `pubspec.yaml` before suggesting new packages.

---
*Initialized by Antigravity AI*
