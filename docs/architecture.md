# Architecture Overview

This document describes the architecture and design of the Decklist to PDF project.

## 🏗️ System Architecture

> [!IMPORTANT]
> **Code Duplication Notice**: The core logic is **duplicated** across implementations, not shared. Each implementation maintains its own copy of the PDF generation logic.

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
├──────────────────┬──────────────────┬───────────────────────────┤
│   Python CLI     │     Dart CLI     │       Flutter GUI         │
│ decklist_to_pdf  │ decklist_to_pdf  │   flutter_app_d2pdf/      │
│      .py         │      .dart       │        lib/               │
└────────┬─────────┴────────┬─────────┴─────────────┬─────────────┘
         │                  │                       │
         ▼                  ▼                       ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────────┐
│  Python Core    │ │   Dart Core     │ │     Flutter Core        │
│  (standalone)   │ │  (standalone)   │ │  (separate copy)        │
│                 │ │                 │ │                         │
│ • PIL/Pillow    │ │ • package:image │ │ • package:image         │
│ • img2pdf       │ │ • package:pdf   │ │ • package:pdf           │
│ • PyPDF2        │ │                 │ │ • package:printing      │
│ • ThreadPool    │ │ • async/await   │ │ • Hive for data         │
└────────┬────────┘ └────────┬────────┘ └────────────┬────────────┘
         │                   │                       │
         └───────────────────┼───────────────────────┘
                             ▼
         ┌────────────────────────────────────────────────────┐
         │                 Shared Resources                   │
         ├────────────────────────────────────────────────────┤
         │  • Scryfall API (card data, images)                │
         │  • Local file system (cache, config, output)       │
         │  • decklist_to_pdf.ini (configuration file)        │
         └────────────────────────────────────────────────────┘
```

## 🔀 Implementation Comparison

| Aspect | Python | Dart CLI | Flutter App |
|--------|--------|----------|-------------|
| **File** | `decklist_to_pdf.py` | `decklist_to_pdf.dart` | `lib/decklist_to_pdf.dart` |
| **Structure** | Top-level functions | Top-level functions | `DecklistToPdfCore` class |
| **Concurrency** | `ThreadPoolExecutor` | `async/await` + `Future.wait` | `async/await` |
| **Image lib** | PIL/Pillow | package:image | package:image |
| **PDF lib** | img2pdf + PyPDF2 | package:pdf | package:pdf + printing |
| **Data storage** | JSON files | JSON files | Hive (binary) |
| **Shared with** | None | None | None |

### Why Duplicated?

1. **Language barrier**: Python logic cannot be directly shared with Dart
2. **Historical**: Dart CLI was ported from Python, Flutter app was created separately
3. **Different dependencies**: Each uses language-specific libraries

### Potential Future Improvement

The Dart CLI and Flutter app could share a common Dart package:

```
Proposed Structure:
├── packages/
│   └── decklist_core/           # Shared Dart package
│       ├── lib/
│       │   └── decklist_core.dart
│       └── pubspec.yaml
├── decklist_to_pdf.dart         # CLI imports decklist_core
└── flutter_app_d2pdf/
    └── lib/
        └── main.dart            # Flutter imports decklist_core
```

## 📦 Component Overview

### 1. Configuration Manager

Handles loading and saving of `decklist_to_pdf.ini`:

```
Configuration Flow:
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│  init_config │ ──▶ │  read_config    │ ──▶ │ conf{} dict  │
└─────────────┘     └─────────────────┘     └──────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  write_config   │
                    │ (missing keys)  │
                    └─────────────────┘
```

### 2. Scryfall Data Loader

Downloads and parses the Scryfall bulk JSON:

```
┌──────────────────┐     ┌────────────────────┐
│  fetch_bulk_json │ ──▶ │ download ~500MB    │
│                  │     │ JSON from Scryfall │
└──────────────────┘     └──────────┬─────────┘
                                    ▼
                         ┌────────────────────┐
                         │ Parse & Filter     │
                         │ (keep needed data) │
                         └──────────┬─────────┘
                                    ▼
                         ┌────────────────────┐
                         │ Save parsed JSON   │
                         │ (faster reload)    │
                         └──────────┬─────────┘
                                    ▼
                         ┌────────────────────┐
                         │ card_data{} dict   │
                         │ key: "set-number"  │
                         └────────────────────┘
```

### 3. Decklist Parser

Processes decklist files into printable card list:

```
Input: "4 Lightning Bolt (2X2) 117"
         │
         ▼
┌────────────────────────────────────┐
│  Parse line components:            │
│  • copies = 4                      │
│  • name = "Lightning Bolt"         │
│  • set = "2x2"                     │
│  • number = "117"                  │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│  Lookup in card_data{}             │
│  key = "2x2-117"                   │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│  Add to decklist[]                 │
│  (with image URIs, layout info)    │
└────────────────────────────────────┘
```

### 4. Image Cache System

Multi-level caching for card images:

```
┌─────────────────────────────────────────────────────────────┐
│                      Image Cache Hierarchy                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Memory Cache (image_cache{})                               │
│        │                                                    │
│        │ miss                                               │
│        ▼                                                    │
│  DPI-Sized Cache (image_cache/<dpi>/<type>/)                │
│  • Gamma-corrected: *_gc.png                                │
│  • Resized: *.png                                           │
│        │                                                    │
│        │ miss                                               │
│        ▼                                                    │
│  Raw Cache (image_cache/<type>/)                            │
│  • Original download from Scryfall                          │
│        │                                                    │
│        │ miss                                               │
│        ▼                                                    │
│  Scryfall API Download                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5. PDF Renderer

Renders card pages and merges to PDF:

```
┌──────────────────────────────────────────────────────────────┐
│                       PDF Rendering Pipeline                  │
└──────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌────────────────────────┐
│  Decklist   │    │  Calculate  │    │  For each page (9      │
│  Cards      │ ──▶│  Total      │ ──▶│  cards):               │
└─────────────┘    │  Pages      │    │  • Create blank A4     │
                   └─────────────┘    │  • Draw background box │
                                      │  • Place 9 card images │
                                      │  • Draw reference marks│
                                      │  • Convert to PDF page │
                                      └───────────┬────────────┘
                                                  │
                                                  ▼
                                      ┌────────────────────────┐
                                      │  Merge all pages       │
                                      │  (in correct order for │
                                      │   two-sided printing)  │
                                      └───────────┬────────────┘
                                                  │
                                                  ▼
                                      ┌────────────────────────┐
                                      │  output/decklist.pdf   │
                                      └────────────────────────┘
```

## 🗂️ Data Structures

### Card Data Dictionary

```python
card_data = {
    "2x2-117": {
        "name": "Lightning Bolt",
        "set": "2x2",
        "collector_number": "117",
        "image_uris": {
            "small": "https://...",
            "normal": "https://...",
            "large": "https://...",
            "png": "https://...",
        },
        "layout": "normal",
        "two_sided": False,
        "border_color": "black"
    },
    
    # Two-sided cards have additional entries
    "mid-47": {
        "name": "Delver of Secrets // Insectile Aberration",
        "layout": "transform",
        "two_sided": True,
        "faces": [card_data["mid-47_A"], card_data["mid-47_B"]]
    },
    "mid-47_A": {
        "name": "Delver of Secrets",
        "image_uris": {...},
        "other_face": "mid-47_B"
    },
    "mid-47_B": {
        "name": "Insectile Aberration",
        "image_uris": {...},
        "other_face": "mid-47_A"
    }
}
```

### Decklist Entry

```python
decklist = [
    {
        "sides": [
            {
                "key": "2x2-117",
                "name": "Lightning Bolt",
                "image_uris": {...},
                "custom": False
            }
        ],
        "two_sided": False,
        "composite": False
    },
    # ...more entries
]
```

### Constants

```python
const = {
    "deck_size": 60,
    "total_pages": 7,
    "card_width_px": 1488,      # at 600 DPI
    "card_height_px": 2079,     # at 600 DPI  
    "page_width_px": 4961,      # A4 at 600 DPI
    "page_height_px": 7016,     # A4 at 600 DPI
    "card_positions_px": [[[x, y], ...], ...],  # 3x3 grid positions
    "marker_rects": [...],      # Reference point rectangles
    "bg_box": [x1, y1, x2, y2], # Background box coordinates
}
```

## 🧵 Concurrency Model

### Python Implementation

Uses `ThreadPoolExecutor` for parallel operations:

```python
# Image downloading
with ThreadPoolExecutor(conf['worker_threads']) as executor:
    for card in decklist:
        executor.submit(fetch_image, url, path, ...)
    
# Page rendering  
with ThreadPoolExecutor(conf['worker_threads']) as executor:
    for page_index in range(total_pages):
        executor.submit(render_page, page_index, side)
```

### Dart Implementation

Uses async/await with parallel futures:

```dart
// Multiple workers process from queue
final workers = List<Future<void>>.generate(
    workerThreads, 
    (_) => worker()
);
await Future.wait(workers);
```

## 📊 Performance Considerations

### Memory Management

| Operation | Memory Usage | Strategy |
|-----------|-------------|----------|
| Scryfall JSON | ~500MB | Parse once, save parsed version |
| Image cache | ~1MB per card | Load on-demand, keep in memory |
| Page rendering | ~50MB per page | Process sequentially at high DPI |

### Optimization Strategies

1. **Parsed JSON caching**: Save processed card data to avoid re-parsing
2. **Multi-level image cache**: Check memory → disk → network
3. **Parallel downloads**: Multiple threads for Scryfall API calls
4. **Streaming PDF output**: Convert pages to PDF as they render

## 🔄 Data Flow Summary

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  INI Config │    │ Scryfall    │    │  Decklist   │
│    File     │    │  Bulk JSON  │    │    File     │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────┐
│                  Initialization                     │
│  • Load config                                      │
│  • Parse/load card data                             │
│  • Parse decklist                                   │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                  Image Collection                   │
│  • Check cache                                      │
│  • Download missing images                          │
│  • Resize to DPI                                    │
│  • Apply gamma correction                           │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                  PDF Generation                     │
│  • Render page images                               │
│  • Convert to PDF                                   │
│  • Merge pages                                      │
│  • Write output file                                │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ output.pdf  │
                   └─────────────┘
```

---

[← Back to Home](README.md)
