# Troubleshooting Guide

Common issues and solutions for Decklist to PDF.

## 🔴 Installation Issues

### Python: "Module not found"

**Problem:** `ModuleNotFoundError: No module named 'PIL'`

**Solution:**
```bash
pip install Pillow requests orjson PyPDF2 img2pdf
```

Or use the setup script:
```bash
./Run.sh  # Linux/macOS
Run.bat   # Windows
```

---

### Dart: "Dependencies not found"

**Problem:** `Could not find package...`

**Solution:**
```bash
dart pub get
```

---

### Flutter: "Hive adapter not found"

**Problem:** `HiveError: Cannot find adapter for type CardModel`

**Solution:**
```bash
dart run build_runner build --delete-conflicting-outputs
```

---

## 🟠 Runtime Errors

### "Card not found in card data"

**Problem:**
```
KeyError: Card "Example Card (SET) 123" not found in card data
```

**Causes & Solutions:**

1. **Typo in set code** - Verify on [scryfall.com](https://scryfall.com)
2. **Wrong collector number** - Check Scryfall for exact number
3. **Outdated data** - Update Scryfall bulk JSON:
   ```
   Do you want to update Scryfall bulk JSON? (y/n): y
   ```
4. **New card** - Wait for Scryfall to update (~24h after release)

---

### "Invalid decklist line"

**Problem:** Line parsing fails

**Check:**
```
✅ 4 Lightning Bolt (2X2) 117
❌ Lightning Bolt (2X2) 117     # Missing count
❌ 4 Lightning Bolt 117         # Missing set
❌ 4 Lightning Bolt (2X2)       # Missing number
```

---

### "Image URL is None"

**Problem:** Card has no image available

**Causes:**
- Promo or special card without image
- Very new card (image not yet uploaded)

**Solution:** Use alternative printing or wait for image

---

### "JSONDecodeError"

**Problem:** Corrupt JSON cache

**Solution:**
```bash
# Delete parsed cache
rm scryfall_bulk_json/parsed_*.json

# Re-run to regenerate
python decklist_to_pdf.py
```

---

### "MemoryError"

**Problem:** Out of memory with large decks at high DPI

**Solutions:**
1. Lower DPI:
   ```ini
   dpi:300
   ```
2. Reduce worker threads:
   ```ini
   worker_threads:2
   ```
3. Process smaller batches

---

## 🟡 Output Issues

### Cards appear washed out

**Problem:** Printed cards have gray borders

**Solution:** Enable gamma correction:
```ini
gamma_correction:True
```

---

### Cards too dark

**Problem:** Colors are oversaturated

**Solution:** Disable gamma correction:
```ini
gamma_correction:False
```

---

### Cards not centered

**Problem:** Print is offset from center

**Solution:** Adjust x-axis offset:
```ini
x_axis_offset:1.5  # Positive = move right
```

Measure offset on test print and adjust accordingly.

---

### Missing reference marks

**Problem:** No cutting guides on output

**Solution:** Enable reference points:
```ini
reference_points:True
```

---

### Two-sided misaligned

**Problem:** Front/back don't line up

**Causes:**
1. Printer has different margins front/back
2. Wrong stagger setting

**Solutions:**
- Calibrate printer margins
- Try toggling stagger:
  ```ini
  stagger:False  # or True
  ```

---

## 🔵 Custom Cards

### Custom card not found

**Problem:** `Custom image not found: custom_cards/Name.png`

**Checklist:**
1. File exists at `custom_cards/Name.png`
2. Filename matches exactly (case-sensitive on Linux/macOS)
3. File is `.png` format
4. Decklist uses `*Name` (not `*Name.png`)

---

### Custom card wrong size

**Problem:** Image stretched or cropped

**Solution:** Use correct dimensions:
- Standard: 745×1040 pixels (for 600 DPI)
- Or: 63×88 mm aspect ratio (1:1.397)

---

## 🟣 Performance

### Downloads very slow

**Solutions:**
1. Increase worker threads:
   ```ini
   worker_threads:8
   ```
2. Use lower quality images for testing:
   ```ini
   image_type:normal
   ```

---

### First run extremely slow

**Normal behavior:** First run parses ~500MB JSON. Subsequent runs use cached parsed version.

**Speed up:**
- Wait for parsing (one-time)
- Don't interrupt the process
- Check `scryfall_bulk_json/parsed_*.json` exists after

---

### PDF generation slow

**Solutions:**
1. Lower DPI for drafts:
   ```ini
   dpi:300
   ```
2. Increase worker threads for rendering

---

## 🔧 Debug Tips

### Enable verbose logging (Python)

```python
logging.basicConfig(level=logging.DEBUG)
```

### Check Dart errors

```bash
dart run decklist_to_pdf.dart 2>&1 | tee debug.log
```

### Flutter DevTools

```bash
flutter run --debug
# Open DevTools URL in browser
```

---

## 📞 Getting Help

If issues persist:

1. Check the card on [scryfall.com](https://scryfall.com)
2. Verify decklist format against examples
3. Try with a minimal decklist (1-2 cards)
4. Check file permissions on cache directories

---

[← Back to Home](README.md)
