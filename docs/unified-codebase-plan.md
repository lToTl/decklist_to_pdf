# Unified Codebase Plan: Dart CLI & Flutter App

This document outlines a plan to further consolidate the codebase architecture.

## Current State

The codebase has already been partially unified:

| File | Purpose |
|------|---------|
| `/flutter_app_d2pdf/lib/decklist_to_pdf.dart` | Core logic (`DecklistToPdfCore` class) |
| `/flutter_app_d2pdf/bin/decklist_to_pdf_cli.dart` | CLI entry point (imports core) |

> [!NOTE]
> The standalone `/decklist_to_pdf.dart` (global functions version) was deprecated and removed in a recent commit. The CLI now imports directly from the Flutter app's library.

The core handles:
- Configuration management
- Scryfall bulk JSON fetching/parsing
- Card data lookup (via `CardDataService`)
- Image downloading/caching
- Gamma correction
- PDF page rendering

## Goals

1. **Single source of truth** for all PDF generation logic
2. **Reduced maintenance burden** - bug fixes and features apply everywhere
3. **Easier testing** - test core logic once
4. **Clean separation** - platform-specific code isolated from business logic

---

## Proposed Architecture

Since the CLI already imports from `flutter_app_d2pdf`, the main refactoring is to extract a **pure Dart core package** that both CLI and Flutter can depend on:

```
decklist_to_pdf/
├── packages/
│   └── d2pdf_core/                   # NEW: Pure Dart core package
│       ├── lib/
│       │   ├── src/
│       │   │   ├── core.dart         # DecklistToPdfCore class
│       │   │   ├── config.dart       # Configuration model & parsing
│       │   │   ├── card_data_provider.dart  # Abstract interface
│       │   │   ├── image_service.dart       # Image handling
│       │   │   ├── pdf_renderer.dart        # PDF generation
│       │   │   └── constants.dart           # Shared constants
│       │   └── d2pdf_core.dart       # Public exports
│       └── pubspec.yaml              # Pure Dart dependencies only
│
├── flutter_app_d2pdf/
│   ├── lib/
│   │   ├── main.dart                 # Flutter UI
│   │   ├── hive_card_data.dart       # Hive-based CardDataProvider impl
│   │   └── data_service.dart         # Existing Hive service
│   ├── bin/
│   │   └── decklist_to_pdf_cli.dart  # CLI entry point (EXISTING)
│   └── pubspec.yaml                  # Depends on d2pdf_core
│
├── python/                           # Python implementation (unchanged)
└── docs/
```

> [!TIP]
> This structure allows the core to be published as a standalone package if desired.

---

## Component Design

### 1. Abstract Card Data Provider

Create an interface that allows different storage backends:

```dart
// lib/src/card_data_provider.dart
abstract class CardDataProvider {
  Future<void> initialize(String bulkJsonPath);
  Map<String, dynamic>? getCardByKey(String key);
  bool containsKey(String key);
  Future<void> dispose();
}
```

**Implementations:**
- `JsonFileCardDataProvider` - For CLI (loads JSON into memory)
- `HiveCardDataProvider` - For Flutter app (uses existing `CardDataService`)

### 2. Unified Configuration

Standardize on a single config format and model:

```dart
// lib/src/config.dart
class DecklistConfig {
  final String decklistPath;
  final bool twoSided;
  final bool customBackside;
  final String backside;
  final String pdfPath;
  final String imageType;
  final int spacing;
  final bool gammaCorrection;
  final bool referencePoints;
  final bool stagger;
  final double xAxisOffset;
  final int workerThreads;
  final int dpi;
  final String bulkJsonPath;
  
  // Factory constructors
  factory DecklistConfig.fromFile(String path);
  factory DecklistConfig.defaults();
  
  // Serialization
  void saveToFile(String path);
}
```

> [!NOTE]
> Recommend standardizing on `.ini` format for backward compatibility with Python script.

### 3. Core Class Refactoring

The `DecklistToPdfCore` class becomes the shared entry point:

```dart
// lib/src/core.dart
class DecklistToPdfCore {
  final DecklistConfig config;
  final CardDataProvider cardDataProvider;
  
  DecklistToPdfCore({
    required this.config,
    required this.cardDataProvider,
  });
  
  Future<void> initialize() async { ... }
  void readDecklist(String filepath) { ... }
  Future<Uint8List> renderPages({...}) async { ... }
}
```

### 4. Image Service

Extract image handling into a dedicated service:

```dart
// lib/src/image_service.dart
class ImageService {
  final DecklistConfig config;
  final Map<String, img.Image> cache = {};
  
  Future<img.Image> fetchImage(String url, String key, {bool custom = false});
  img.Image applyGammaCorrection(img.Image image, {double gamma = 2.2});
  void clearCache();
}
```

---

## Migration Steps

### Phase 1: Create Shared Package Structure

1. Create `lib/` directory with package structure
2. Create `lib/decklist_to_pdf.dart` with public exports
3. Update root `pubspec.yaml` to define the package

### Phase 2: Extract Core Logic

1. Move `DecklistToPdfCore` from Flutter app to `lib/src/core.dart`
2. Create `CardDataProvider` abstract class
3. Extract `DecklistConfig` model
4. Extract `ImageService`
5. Extract `PdfRenderer`

### Phase 3: Create Provider Implementations

1. Create `JsonFileCardDataProvider` for CLI use
2. Create `HiveCardDataProvider` wrapping existing `CardDataService`

### Phase 4: Update Consumers

1. **CLI** (`flutter_app_d2pdf/bin/decklist_to_pdf_cli.dart`):
   ```dart
   import 'package:d2pdf_core/d2pdf_core.dart';
   
   void main(List<String> args) async {
     final config = DecklistConfig.fromFile('decklist_to_pdf.ini');
     final provider = JsonFileCardDataProvider();
     final core = DecklistToPdfCore(config: config, cardDataProvider: provider);
     // Parse args, run generation...
   }
   ```

2. **Flutter App** (`flutter_app_d2pdf/lib/main.dart`):
   ```dart
   import 'package:d2pdf_core/d2pdf_core.dart';
   
   // Use HiveCardDataProvider with existing CardDataService
   final provider = HiveCardDataProvider(CardDataService.instance);
   final core = DecklistToPdfCore(config: config, cardDataProvider: provider);
   ```

3. Update `flutter_app_d2pdf/pubspec.yaml`:
   ```yaml
   dependencies:
     d2pdf_core:
       path: ../packages/d2pdf_core
   ```

### Phase 5: Cleanup

1. Delete `/flutter_app_d2pdf/lib/decklist_to_pdf.dart` (move to core package)
2. Update imports throughout the Flutter app
3. Update documentation

---

## Breaking Changes

| Change | Impact | Mitigation |
|--------|--------|------------|
| Config file format | Users may need to update | Provide migration script or support both |
| Import paths | Internal only | Update all imports during refactor |
| Flutter app internal | No user impact | None needed |

> [!NOTE]
> Since the CLI already uses the Flutter app's core, the CLI invocation remains unchanged.

---

## Testing Strategy

1. **Unit Tests**: Test each extracted component in isolation
2. **Integration Tests**: Test full PDF generation flow
3. **Comparison Tests**: Generate PDFs with old and new code, compare output

---

## Estimated Effort

| Phase | Estimated Time |
|-------|---------------|
| Phase 1: Package Structure | 1-2 hours |
| Phase 2: Extract Core Logic | 2-3 hours |
| Phase 3: Provider Implementations | 2-3 hours |
| Phase 4: Update Consumers | 1-2 hours |
| Phase 5: Cleanup & Testing | 2-3 hours |
| **Total** | **8-13 hours** |

> [!TIP]
> The reduced estimate reflects that the CLI already imports from the Flutter library, so less migration work is needed.

---

## Open Questions

1. **Config format**: Keep `.ini` for Python compatibility or switch to `.conf`/`.yaml`?
2. **Package location**: Use `packages/d2pdf_core` or keep core in `flutter_app_d2pdf/lib`?
3. **Package naming**: Use `d2pdf_core` or another name?

---

*Document created: December 2025*
