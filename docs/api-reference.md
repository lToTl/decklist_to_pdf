# API Reference

Documentation of key functions and classes across all implementations.

## 📦 Python API (`decklist_to_pdf.py`)

### Configuration

| Function | Description |
|----------|-------------|
| `init_config()` | Initialize config with defaults, load from INI |
| `read_config()` | Load settings from `decklist_to_pdf.ini` |
| `write_config(conf_list)` | Write config entries to INI file |

### Data Loading

| Function | Returns | Description |
|----------|---------|-------------|
| `fetch_bulk_json(ask)` | `str` | Download Scryfall JSON, return path |
| `load_card_dictionary()` | `dict` | Parse JSON to searchable dict |
| `card_data_lookup(line)` | `dict` | Look up card from decklist line |

### Decklist

| Function | Description |
|----------|-------------|
| `read_decklist(filepath)` | Parse decklist file into global list |
| `add_card_data_to_decklist(card)` | Add card to print queue |

### Images

| Function | Description |
|----------|-------------|
| `create_image_cache()` | Download all needed images (parallel) |
| `fetch_image(url, dest, headers, key, custom)` | Download/cache single image |
| `resize_image_to_card_size(img, dpi)` | Resize to card dimensions |

### PDF

| Function | Returns | Description |
|----------|---------|-------------|
| `generate_constants()` | `dict` | Calculate layout values |
| `render_page(page_idx, side)` | - | Render one 9-card page |
| `render_pages()` | - | Render all pages |
| `merge_pages()` | - | Combine into final PDF |

---

## 🎯 Dart API (`decklist_to_pdf.dart`)

### DecklistToPdfCore Class

```dart
class DecklistToPdfCore {
  final conf = <String, dynamic>{};
  final cardData = <String, dynamic>{};
  final decklist = <Map<String, dynamic>>[];
  final imageCache = <String, img.Image>{};
  late Map<String, dynamic> consts;
}
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `setupWorkspace()` | `Future<void>` | Create directories |
| `initConfig({override})` | `void` | Initialize config |
| `initialize({fetchBulk})` | `Future<void>` | Full initialization |
| `fetchBulkJson({ask})` | `Future<String>` | Download Scryfall data |
| `loadCardDictionary(path)` | `Map` | Parse card database |
| `cardDataLookup(line)` | `Map` | Look up card data |
| `readDecklist(path)` | `void` | Parse decklist |
| `fetchImage(...)` | `Future<void>` | Download/cache image |
| `applyGammaCorrection(img)` | `img.Image` | Apply gamma correction |
| `createImageCache()` | `Future<void>` | Download all images |
| `renderPages({...})` | `Future<Uint8List>` | Generate PDF bytes |

---

## 📱 Flutter API

### MyAppState (ChangeNotifier)

| Method | Description |
|--------|-------------|
| `clearDeck()` | Clear all cards |
| `setDeck(path)` | Load decklist from file |
| `addCopy(index)` | Duplicate card |
| `addCard(item, index)` | Insert card |
| `removeCard(index)` | Remove card |
| `moveCard(old, new)` | Reorder card |
| `updateConfig(key, val)` | Update setting |

### CardDataService

| Method | Returns | Description |
|--------|---------|-------------|
| `initializeAndLoadData(path)` | `Future<void>` | Initialize Hive |
| `getAllCards()` | `Future<List<CardModel>>` | Get all cards |

---

## 🔢 Constants

| Constant | Value | Unit |
|----------|-------|------|
| Card Width | 63 | mm |
| Card Height | 88 | mm |
| A4 Width | 210 | mm |
| A4 Height | 297 | mm |
| Cards/Page | 9 | - |

### At 600 DPI

| Constant | Pixels |
|----------|--------|
| Card Width | 1488 |
| Card Height | 2079 |
| Page Width | 4961 |
| Page Height | 7016 |

---

[← Back to Home](README.md)
