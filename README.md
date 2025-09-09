# decklist_to_pdf
Python script to generate printable pdf file from MTG decklist

Needs Python 3.10 or newer

---

## Dart translation

This repository also contains a pragmatic Dart translation of `decklist_to_pdf.py` at `decklist_to_pdf.dart`.

What it does (simplified):
- Loads Scryfall bulk JSON (downloaded to `scryfall_bulk_json/`).
- Reads a decklist file (`decklist.txt` or `input/<name>.txt`).
- Downloads card images into `image_cache/<type>/` and resizes them.
- Renders pages of 9 cards to an A4 PDF using the `pdf` package.

Quick start (Dart):

```powershell
dart pub get
dart run decklist_to_pdf.dart
```

Notes and limitations:
- The Dart translation focuses on structure and common flows. Advanced features from the Python original (gamma correction loops, complex two-sided staggering, some error handling details) are simplified.
- Output PDF is written to `output/Output.pdf`.
- Dependencies are in `pubspec.yaml`.

If you'd like, I can add more exact parity for gamma correction and two-sided printing, or implement concurrent image downloads.
