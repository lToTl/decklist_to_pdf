# Dart CLI Documentation

The Dart CLI (`decklist_to_pdf.dart`) is a port of the Python script to Dart, offering similar functionality with Dart's async features.

## 📋 Requirements

- Dart SDK 2.17 or newer
- Dependencies (from `pubspec.yaml`):
  - `http` - HTTP client for API requests
  - `image` - Image processing library
  - `pdf` - PDF generation
  - `path` - Path manipulation utilities

## 🚀 Quick Start

### Install Dependencies

```bash
dart pub get
```

### Run the Script

```bash
dart run decklist_to_pdf.dart
```

Or compile and run:

```bash
dart compile exe decklist_to_pdf.dart
./decklist_to_pdf.exe
```

## 📖 Command-Line Arguments

```bash
dart decklist_to_pdf.dart [OPTIONS]
```

### Available Options

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--help` | `-h` | flag | Show help message |
| `--input` | `-i` | string | Decklist name (without `.txt`) |
| `--output` | `-o` | string | Output PDF name (without `.pdf`) |
| `--two-sided` | `-t` | bool | Enable two-sided printing |
| `--custom-backside` | `-c` | bool | Use custom card back |
| `--backside` | `-b` | string | Custom back image filename |
| `--image-type` | `-f` | string | Scryfall image type |
| `--spacing` | `-p` | float | Card spacing in mm |
| `--mode` | `-m` | string | Layout mode |
| `--gamma-correction` | `-g` | bool | Enable gamma correction |
| `--reference-points` | `-r` | bool | Show reference points |
| `--stagger` | `-s` | bool | Stagger pages for printing |
| `--x-axis-offset` | `-x` | float | Horizontal offset in mm |
| `--dpi` | `-d` | int | Rendering DPI |
| `--worker-threads` | `-w` | int | Parallel download threads |

### Examples

```bash
# Basic usage with decklist name
dart decklist_to_pdf.dart -i my_deck

# Two-sided printing at 300 DPI
dart decklist_to_pdf.dart -i my_deck -t true -d 300

# Custom output name with gamma correction off
dart decklist_to_pdf.dart -i my_deck -o print_ready -g false

# High-quality with more download threads
dart decklist_to_pdf.dart -i my_deck -d 600 -w 8
```

## 🏗️ Architecture

### Main Class: DecklistToPdfCore

The Dart implementation uses a class-based structure:

```dart
class DecklistToPdfCore {
  // Configuration
  final conf = <String, dynamic>{};
  final cardData = <String, dynamic>{};
  final decklist = <Map<String, dynamic>>[];
  final imageCache = <String, img.Image>{};
  late Map<String, dynamic> consts;
  
  // Methods
  void initConfig();
  Future<String> fetchBulkJson();
  Map<String, dynamic> loadCardDictionary(String path);
  void readDecklist(String filepath);
  Future<Uint8List> renderPages();
  // ...
}
```

### Key Differences from Python

| Feature | Python | Dart |
|---------|--------|------|
| Concurrency | ThreadPoolExecutor | async/await + Future.wait |
| JSON parsing | orjson | dart:convert |
| Image processing | PIL/Pillow | package:image |
| PDF generation | img2pdf + PyPDF2 | package:pdf |

## 🔧 Core Functions

### Configuration

```dart
void initConfig({Map<String, dynamic>? overrideConfig})
```
Initialize configuration with defaults and optionally override settings.

```dart
void readConfig()
```
Load settings from `decklist_to_pdf.ini`.

### Data Loading

```dart
Future<String> fetchBulkJson({bool ask = true})
```
Download Scryfall bulk JSON data. Returns path to downloaded file.

```dart
Map<String, dynamic> loadCardDictionary(String filepath)
```
Parse Scryfall JSON into searchable card data dictionary.

### Decklist Processing

```dart
Map<String, dynamic> cardDataLookup(String decklistLine)
```
Parse a decklist line and look up card data.

```dart
void readDecklist(String filepath)
```
Read and parse entire decklist file.

### Image Handling

```dart
Future<void> fetchImage(
  String imageUrl, 
  String destination, 
  String key, 
  bool custom
)
```
Download and cache a card image.

```dart
img.Image applyGammaCorrection(img.Image image, {double gamma = 2.2})
```
Apply gamma correction for better print quality.

### PDF Generation

```dart
Map<String, dynamic> generateConstants()
```
Calculate page layout constants based on configuration.

```dart
Future<Uint8List> renderPages({
  String? decklistName,
  bool? twoSided,
  bool? stagger,
})
```
Render all pages and return PDF as bytes.

## 📊 Data Structures

### Configuration Dictionary

```dart
conf = {
  'decklist_path': 'decklist.txt',
  'two_sided': false,
  'custom_backside': false,
  'backside': 'back.png',
  'pdf_path': 'output',
  'image_type': 'png',
  'spacing': 0,
  'mode': 'default',
  'gamma_correction': true,
  'reference_points': true,
  'stagger': true,
  'x_axis_offset': 0.75,
  'dpi': 300,
  'worker_threads': 4,
};
```

### Card Data Entry

```dart
cardData['set-number'] = {
  'name': 'Card Name',
  'set': 'set',
  'collector_number': 'number',
  'image_uris': {
    'small': 'url',
    'normal': 'url',
    'large': 'url',
    'png': 'url',
  },
  'layout': 'normal',
  'two_sided': false,
  'border_color': 'black'
};
```

## ⚡ Async Image Download System

The Dart version uses a queue-based worker system:

```dart
Future<void> createImageCache() async {
  final entriesQueue = Queue<MapEntry<String, Map<String, dynamic>>>.from(
    keysToFetch.entries
  );
  
  Future<void> worker() async {
    while (entriesQueue.isNotEmpty) {
      final entry = entriesQueue.removeFirst();
      await fetchImage(url, destination, key, custom);
    }
  }
  
  final workers = List<Future<void>>.generate(
    workerThreads, 
    (_) => worker()
  );
  await Future.wait(workers);
}
```

This provides parallel downloads while respecting worker thread limits.

## 🎨 Gamma Correction

```dart
img.Image applyGammaCorrection(img.Image image, {double gamma = 2.2}) {
  final corrected = img.Image.from(image);
  for (int y = 0; y < corrected.height; y++) {
    for (int x = 0; x < corrected.width; x++) {
      final c = corrected.getPixel(x, y);
      int correct(int v) =>
          (255 * math.pow(v / 255, 1 / gamma)).clamp(0, 255).toInt();
      corrected.setPixelRgba(x, y, 
        correct(getRed(c)), 
        correct(getGreen(c)), 
        correct(getBlue(c)), 
        getAlpha(c)
      );
    }
  }
  return corrected;
}
```

## 📄 PDF Rendering

The Dart version uses the `pdf` package for native PDF generation:

```dart
final outPdf = pw.Document();

// For each page
final pwImage = pw.MemoryImage(pngBytes);
outPdf.addPage(pw.Page(
  build: (context) => pw.Center(child: pw.Image(pwImage)),
  pageFormat: pdf.PdfPageFormat(a4Width, a4Height),
));

return outPdf.save();  // Returns Uint8List
```

## 🔍 Error Handling

```dart
try {
  await fetchImage(url, destination, key, custom);
} catch (e) {
  stderr.writeln('Download failed for $key: $e');
}
```

Common errors:
- `Exception: Card not found` - Invalid set/collector number
- `Exception: Failed to download` - Network error
- `Exception: Bulk json not found` - Missing Scryfall data

## 💻 Example Session

```bash
$ dart run decklist_to_pdf.dart -i burn_deck -d 300

Starting decklist_to_pdf in Dart
Loading configuration from decklist_to_pdf.ini
Trying png image for key 2x2-117 -> https://...
Image already cached for cmm-81 -> image_cache/png/png/cmm-81.png
...
PDF created at output/burn_deck.pdf
```

## 📁 Output

Generated PDFs are saved to:
```
output/<decklist_name>.pdf
```

The Dart version outputs to the same location as the Python version, ensuring compatibility.

---

[← Python Script](python-script.md) | [Back to Home](README.md) | [Flutter App →](flutter-app.md)
