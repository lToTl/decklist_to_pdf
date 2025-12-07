# Python Script Documentation

The Python script (`decklist_to_pdf.py`) is the original implementation of the Decklist to PDF tool.

## 📋 Requirements

- Python 3.10 or newer
- Required packages:
  - `Pillow` - Image processing
  - `requests` - HTTP requests
  - `orjson` - Fast JSON parsing
  - `PyPDF2` - PDF merging
  - `img2pdf` - Image to PDF conversion

## 🚀 Quick Start

### Using Run Script

```bash
# Linux/macOS
./Run.sh

# Windows
Run.bat
```

### Manual Execution

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Run the script
python decklist_to_pdf.py
```

## 📖 Interactive Prompts

When you run the script, you'll be asked:

1. **Update Scryfall data?**
   ```
   Do you want to update Scryfall bulk JSON? (y/n):
   ```

2. **Decklist name:**
   ```
   Enter decklist name (default: decklist.txt):
   ```
   - Press Enter for default
   - Enter a name (e.g., `my_deck`) to use `input/my_deck.txt`

## 🔧 Main Functions

### Configuration

| Function | Description |
|----------|-------------|
| `init_config()` | Initialize configuration with defaults |
| `read_config()` | Load settings from `decklist_to_pdf.ini` |
| `write_config(conf_list)` | Write/append config entries to INI file |

### Data Loading

| Function | Description |
|----------|-------------|
| `fetch_bulk_json(ask)` | Download Scryfall bulk JSON |
| `load_card_dictionary()` | Parse JSON into card data dict |
| `card_data_lookup(line)` | Find card data from decklist line |

### Decklist Processing

| Function | Description |
|----------|-------------|
| `read_decklist(filepath)` | Parse decklist file |
| `add_card_data_to_decklist(card)` | Add card to print queue |

### Image Handling

| Function | Description |
|----------|-------------|
| `create_image_cache()` | Download all needed images |
| `fetch_image(url, dest, headers, key, custom)` | Download/cache single image |
| `resize_image_to_card_size(image, dpi)` | Resize to output dimensions |

### PDF Generation

| Function | Description |
|----------|-------------|
| `generate_constants()` | Calculate page layout values |
| `render_page(page_index, side)` | Render one page of cards |
| `render_pages()` | Render all pages |
| `merge_pages()` | Combine pages into final PDF |

## 📊 Global Variables

```python
conf = {}           # Configuration dictionary
card_data = {}      # Scryfall card data
decklist = []       # Parsed decklist entries
const = {}          # Layout constants
image_cache = {}    # In-memory image cache
pages = {}          # Rendered page buffers
```

## 🖼️ Image Processing Pipeline

```
Scryfall Download
       │
       ▼
┌─────────────────────────────────┐
│  Save to image_cache/<type>/   │
│  (original resolution)          │
└─────────────────┬───────────────┘
                  │
                  ▼
┌─────────────────────────────────┐
│  Resize to DPI                  │
│  63mm × 88mm at configured DPI  │
│  Save to image_cache/<dpi>/    │
└─────────────────┬───────────────┘
                  │
                  ▼
┌─────────────────────────────────┐
│  Gamma Correction               │
│  Adjust contrast for printing   │
│  Save as *_gc.png              │
└─────────────────┬───────────────┘
                  │
                  ▼
┌─────────────────────────────────┐
│  Load to Memory                 │
│  Add to image_cache{}          │
└─────────────────────────────────┘
```

### Gamma Correction Algorithm

The gamma correction improves print quality by adjusting dark borders:

```python
def correct_image_gamma():
    # Sample border color from bottom edge
    border_color = img.getpixel((width/2, height - height/50))
    border_gamma = sum(border_color[:3]) / 3
    
    # Enhance contrast until border is truly black
    while border_gamma > 3:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1 + border_gamma / 256)
        # Re-sample and repeat
```

## 📄 Page Layout

### Card Dimensions

| Measurement | Value |
|-------------|-------|
| Card width | 63 mm |
| Card height | 88 mm |
| Page size | A4 (210 × 297 mm) |
| Cards per page | 9 (3×3 grid) |

### Layout Calculation

```python
# Convert mm to pixels
mm_to_px = lambda val_mm: int(val_mm * dpi / 25.4)

# Grid dimensions
grid_width = 3 * card_width + 2 * spacing
grid_height = 3 * card_height + 2 * spacing

# Center on page with offset
grid_x_offset = (page_width - grid_width) / 2 + x_axis_offset
grid_y_offset = (page_height - grid_height) / 2
```

## 🖨️ Two-Sided Printing Logic

### Page Ordering

**Standard (stagger=False):**
```
Page 1 Front, Page 1 Back, Page 2 Front, Page 2 Back, ...
```

**Staggered (stagger=True):**
```
Page 1 Front, Page 2 Front, Page 1 Back, Page 2 Back, ...
```

### Back Side Alignment

For two-sided printing, back side cards are horizontally mirrored:

```python
if side == 1:  # Back side
    x_index = 2 - col_index  # Flip column position
```

## ⚡ Performance Features

### Concurrent Image Downloads

```python
with ThreadPoolExecutor(conf['worker_threads']) as executor:
    for card in decklist:
        futures.append(
            executor.submit(fetch_image, url, dest, ...)
        )
        if not os.path.exists(dest):
            sleep(0.1)  # Rate limiting for Scryfall API
```

### Concurrent Page Rendering

```python
with ThreadPoolExecutor(max_workers=conf['worker_threads']) as executor:
    for i in range(total_pages):
        executor.submit(render_page, i, 0)  # Front
    if conf['two_sided']:
        for i in range(total_pages):
            executor.submit(render_page, i, 1)  # Back
```

## 📝 Output

### Logging

The script uses Python's `logging` module:

```python
logging.basicConfig(level=logging.INFO)
```

Log messages include:
- Configuration loading status
- Scryfall data download progress
- Image download/cache status
- Page rendering times
- PDF generation completion

### Output Location

Generated PDFs are saved to:
```
output/<decklist_name>.pdf
```

## 🔍 Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Decklist not found | Check path in `input/` |
| `KeyError: Card not found` | Invalid set/number | Verify Scryfall data |
| `JSONDecodeError` | Corrupt cache | Delete parsed JSON cache |
| `MemoryError` | Large deck/high DPI | Reduce DPI or deck size |

## 💻 Example Session

```
$ python decklist_to_pdf.py
INFO:root:Loading configuration from decklist_to_pdf.ini
Do you want to update Scryfall bulk JSON? (y/n): n
INFO:root:Skipping Scryfall bulk JSON download.
INFO:root:Loading Scryfall bulk json to dictionary from scryfall_bulk_json/default-cards-20251207.json
scryfall_bulk_json/parsed_default-cards-20251207.json
Loading parsed JSON...
INFO:root:Loaded 82453 cards from scryfall_bulk_json/default-cards-20251207.json
INFO:root:Finished in 1.23 seconds
Enter decklist name (default: decklist.txt): my_burn_deck
INFO:root:Reading decklist from input/my_burn_deck.txt
INFO:root:Found 75 cards to print in decklist
INFO:root:Creating PDF
INFO:root:Loading Images into cache...
INFO:root:Downloaded 23 new images
INFO:root:Image cache created in 4.56 seconds.
INFO:root:Rendering pages as images...
INFO:root:Rendering page 0 front
...
INFO:root:Merging pages into PDF
INFO:root:PDF created successfully at output/my_burn_deck.pdf
INFO:root:Finished in 12.34 seconds
```

---

[← Back to Home](README.md) | [Dart CLI →](dart-cli.md)
