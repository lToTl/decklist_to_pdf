# Flutter App Documentation

The Flutter app (`flutter_app_d2pdf`) provides a cross-platform GUI for creating printable MTG decklists.

## 📋 Requirements

- Flutter SDK 3.9+
- Dart SDK (included with Flutter)
- Platform-specific build tools:
  - **Windows**: Visual Studio with C++ tools
  - **macOS**: Xcode
  - **Linux**: GTK3 development libraries
  - **Android**: Android SDK
  - **iOS**: Xcode + CocoaPods

## 🚀 Quick Start

### Installation

```bash
cd flutter_app_d2pdf

# Get dependencies
flutter pub get

# Generate Hive type adapters
dart run build_runner build
```

### Running the App

```bash
# Debug mode
flutter run

# Specific platform
flutter run -d windows
flutter run -d macos
flutter run -d linux
flutter run -d chrome  # Web
```

### Building for Production

```bash
# Windows
flutter build windows

# macOS
flutter build macos

# Linux
flutter build linux

# Android
flutter build apk

# iOS
flutter build ios

# Web
flutter build web
```

## 🏗️ Project Structure

```
flutter_app_d2pdf/
├── lib/
│   ├── main.dart              # App entry, UI components
│   ├── decklist_to_pdf.dart   # Core PDF generation logic
│   ├── card_data_model.dart   # Hive data models
│   ├── card_data_model.g.dart # Generated Hive adapters
│   └── data_service.dart      # Hive data service
├── android/                   # Android platform code
├── ios/                       # iOS platform code
├── linux/                     # Linux platform code
├── macos/                     # macOS platform code
├── web/                       # Web platform code
├── windows/                   # Windows platform code
└── pubspec.yaml               # Dependencies
```

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `flutter` | UI framework |
| `provider` | State management |
| `http` | HTTP requests |
| `image` | Image processing |
| `pdf` | PDF generation |
| `printing` | Print preview/export |
| `file_picker` | File selection dialog |
| `super_clipboard` | Clipboard support |
| `hive` / `hive_flutter` | Fast local data storage |
| `path_provider` | Platform paths |

## 🎨 UI Components

### MyApp (Main Application)

The root widget that sets up providers and theming:

```dart
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => MyAppState(),
      child: MaterialApp(
        title: 'Decklist to PDF',
        home: PageFolder(),
      ),
    );
  }
}
```

### MyAppState (State Management)

Central state management using Provider:

```dart
class MyAppState extends ChangeNotifier {
  void clearDeck();
  void setDeck(String path);
  void addCopy(int index);
  void addCard(Map<String, dynamic> item, int index);
  void removeCard(int index);
  void moveCard(int oldIndex, int newIndex);
  void updateConfig(String key, dynamic value);
}
```

### PageFolder (Navigation)

Tab-based navigation between app sections:

- **DeckBuilder**: Manage decklist cards
- **PrintingPage**: Configure and generate PDF

### DeckBuilder

Interface for building and editing decklists:

- Add/remove cards
- Drag to reorder
- Duplicate cards
- Import from file

### PrintingPage

PDF configuration and preview:

- Configuration options
- Live page preview
- Print/export functionality

### PagePreview

Real-time preview of card layout:

```dart
class _PagePreviewState extends State<PagePreview> {
  Future<void> _loadUiImages() async {
    // Load card images for preview
  }
  
  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _PagePainter(
        images: _uiImages,
        // layout parameters
      ),
    );
  }
}
```

### _PagePainter (Custom Rendering)

Custom painter for drawing card pages:

```dart
class _PagePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    // Draw background
    // Draw card images in 3x3 grid
    // Draw reference marks
  }
}
```

## 💾 Data Layer

### CardModel (Hive Model)

Data model for Scryfall card data:

```dart
@HiveType(typeId: 0)
class CardModel extends HiveObject {
  @HiveField(0)
  late String id;
  
  @HiveField(1)
  late String name;
  
  @HiveField(2)
  Map<String, String>? imageUris;
  
  // ... more fields
}
```

### CardDataService

Service for loading and querying card data:

```dart
class CardDataService {
  static Future<void> initializeAndLoadData(String assetPath) async {
    await Hive.initFlutter();
    Hive.registerAdapter(CardModelAdapter());
    // Parse JSON and save to Hive (one-time)
  }
  
  static Future<List<CardModel>> getAllCards() async {
    final box = await Hive.openBox<CardModel>(_kCardBox);
    return box.values.toList();
  }
}
```

### Data Storage Strategy

```
First Launch (Slow):
┌──────────────────┐     ┌──────────────────┐
│  Load JSON asset │ ──▶ │  Parse to models │
│  (~500MB)        │     │                  │
└──────────────────┘     └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Save to Hive    │
                         │  (binary format) │
                         └──────────────────┘

Subsequent Launches (Fast):
┌──────────────────┐
│  Load from Hive  │ ──▶ Ready in seconds
│  (binary format) │
└──────────────────┘
```

## 📄 DecklistToPdfCore

Shared core logic used by both CLI and Flutter:

```dart
class DecklistToPdfCore {
  final conf = <String, dynamic>{};
  final cardData = <String, dynamic>{};
  final decklist = <Map<String, dynamic>>[];
  final imageCache = <String, img.Image>{};
  
  Future<void> setupWorkspace();
  void initConfig({Map<String, dynamic>? overrideConfig});
  Future<void> initialize({bool fetchBulk = true});
  Future<Uint8List> renderPages({...});
}
```

## 🖨️ Printing Integration

Using the `printing` package for cross-platform print support:

```dart
import 'package:printing/printing.dart';

// Print directly
await Printing.layoutPdf(
  onLayout: (format) async => pdfBytes,
);

// Share/export
await Printing.sharePdf(
  bytes: pdfBytes,
  filename: 'decklist.pdf',
);

// Print preview
Printing.directPrintPdf(
  printer: printer,
  onLayout: (format) async => pdfBytes,
);
```

## ⚙️ Configuration Binding

UI elements bound to configuration:

```dart
Switch(
  value: appState.config['two_sided'] ?? false,
  onChanged: (value) {
    appState.updateConfig('two_sided', value);
  },
)
```

## 🎯 Feature Highlights

### Drag and Drop Reordering

```dart
ReorderableListView.builder(
  onReorder: (oldIndex, newIndex) {
    appState.moveCard(oldIndex, newIndex);
  },
  // ...
)
```

### File Picker Integration

```dart
FilePickerResult? result = await FilePicker.platform.pickFiles(
  type: FileType.custom,
  allowedExtensions: ['txt'],
);
```

### Clipboard Support

```dart
final clipboard = SystemClipboard.instance;
if (clipboard != null) {
  final reader = await clipboard.read();
  // Process clipboard content
}
```

## 🐛 Debugging

### Debug Build

```bash
flutter run --debug
```

### Verbose Logging

```dart
stderr.writeln('Debug: $message');
```

### DevTools

```bash
flutter run --debug
# Then open DevTools in browser
```

## 📱 Platform-Specific Notes

### Android

- Minimum SDK: 21 (Android 5.0)
- Internet permission required for image downloads

### iOS

- Minimum iOS: 12.0
- App Transport Security configured for HTTP

### Desktop (Windows/macOS/Linux)

- File system access for cache directories
- Native print dialogs

### Web

- Limited file system access
- Uses browser print functionality

## 💡 Development Tips

### Hot Reload

Press `r` in terminal or use IDE button for hot reload.

### Generate Hive Adapters

After modifying `CardModel`:

```bash
dart run build_runner build --delete-conflicting-outputs
```

### Clean Build

```bash
flutter clean
flutter pub get
dart run build_runner build
flutter run
```

---

[← Dart CLI](dart-cli.md) | [Back to Home](README.md)
