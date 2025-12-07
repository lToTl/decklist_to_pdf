# Configuration Guide

All settings are stored in `decklist_to_pdf.ini`. The file is created automatically on first run with default values.

## 📄 Configuration File Format

```ini
# Lines starting with # are comments
key:value
```

## ⚙️ All Configuration Options

### File Paths

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `decklist_path` | string | `decklist.txt` | Path to the default decklist file |
| `pdf_path` | string | `output.pdf` | Default output PDF path |
| `bulk_json_path` | string | *(auto)* | Path to Scryfall bulk JSON file |

### Image Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `image_type` | string | `png` | Image quality to download |
| `dpi` | integer | `600` | Pixel density for rendering |
| `gamma_correction` | boolean | `True` | Adjust image contrast/gamma |

**Image Type Options:**

| Type | Resolution | File Size | Use Case |
|------|-----------|-----------|----------|
| `small` | 146×204 | ~10KB | Preview only |
| `normal` | 488×680 | ~50KB | Screen viewing |
| `large` | 672×936 | ~100KB | Standard printing |
| `png` | 745×1040 | ~400KB | High-quality printing |
| `art_crop` | Varies | Varies | Art only, no borders |
| `border_crop` | Varies | Varies | Cropped borders |

### Page Layout

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `spacing` | integer | `0` | Gap between cards in mm |
| `x_axis_offset` | float | `0.75` | Horizontal offset in mm |
| `reference_points` | boolean | `True` | Show CNC locator marks |
| `mode` | string | `default` | Layout mode |

**Layout Modes:**

| Mode | Card Size | Description |
|------|----------|-------------|
| `default` | 63×88 mm | Standard MTG size with 2mm black border |
| `bleed_edge` | 65×90.79 mm | Full bleed for borderless cards |

### Two-Sided Printing

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `two_sided` | boolean | `False` | Enable two-sided output |
| `custom_backside` | boolean | `False` | Use custom back image |
| `backside` | string | `back.png` | Custom back image filename |
| `stagger` | boolean | `True` | Stagger pages for slow printers |

**Page Order with Staggering:**

| Setting | Page Order | Best For |
|---------|------------|----------|
| `stagger:True` | Front1, Front2, Back1, Back2 | Slow printers with dry time |
| `stagger:False` | Front1, Back1, Front2, Back2 | Fast duplex printers |

### Performance

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `worker_threads` | integer | `4` | Parallel image download threads |

### HTTP Headers

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `user_agent` | string | `decklist_to_pdf/0.1` | User-Agent for Scryfall API |
| `accept` | string | `application/json;q=0.9,*/*;q=0.8` | Accept header |

## 📝 Example Configuration

```ini
# relative path to scryfall bulk json file
bulk_json_path:scryfall_bulk_json/default-cards-20251207.json

# relative path to decklist
decklist_path:input/my_deck.txt

# two sided printing
two_sided:True

# has custom backside
custom_backside:False

# default backside image
backside:back.png

# possible image types are small / normal / large / png / art_crop / border_crop
image_type:png

# spacing between cards in mm
spacing:0

# layout mode
mode:default

# gamma correction for images
gamma_correction:True

# toggle reference point True/False
reference_points:True

# stagger pages for faster 2 sided printing
stagger:True

# move everything on the x_axis
x_axis_offset:0.75

# pixel density for printing
dpi:600

# number of worker threads
worker_threads:4
```

## 🔧 Common Configuration Scenarios

### High-Quality Prints

```ini
image_type:png
dpi:600
gamma_correction:True
```

### Fast Preview/Testing

```ini
image_type:normal
dpi:300
gamma_correction:False
worker_threads:8
```

### Two-Sided with Custom Backs

```ini
two_sided:True
custom_backside:True
backside:my_custom_back.png
stagger:True
```

Place `my_custom_back.png` in the `cardbacks/` folder.

### Professional Print Shop

```ini
image_type:png
dpi:600
reference_points:True
spacing:0
mode:default
```

### Borderless Cards

```ini
mode:bleed_edge
spacing:0
```

## 🖨️ Printer Offset Calibration

If your printer doesn't center the output correctly:

1. Print a test page with `reference_points:True`
2. Measure the offset from expected position
3. Adjust `x_axis_offset` value (in mm)
   - Positive values move content right
   - Negative values move content left

Example for a printer that prints 1.5mm too far left:
```ini
x_axis_offset:1.5
```

## 💡 Tips

### Gamma Correction

Enable `gamma_correction:True` if:
- Cards appear washed out when printed
- Black borders look gray
- You're using a laser printer

Disable if:
- Colors appear too dark
- You're using a high-quality inkjet

### Worker Threads

- Increase for faster downloads (if you have good internet)
- Decrease if you get rate-limited by Scryfall
- Recommended: 4-8 threads

### DPI Selection

| DPI | File Size | Use Case |
|-----|----------|----------|
| 300 | Small | Draft/testing |
| 450 | Medium | Standard home printing |
| 600 | Large | Professional quality |

---

[← Back to Home](README.md) | [Decklist Format →](decklist-format.md)
