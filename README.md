# decklist_to_pdf
Python script to generate printable pdf file from MTG decklist
WIP dart version and flutter gui.
Needs Python 3.10 or newer

---

## Dart translation

This repository also contains a pragmatic Dart translation of `decklist_to_pdf.py` at `decklist_to_pdf.dart`.

What it does (simplified):
- Loads Scryfall bulk JSON (downloaded to `scryfall_bulk_json/`).
- Reads a decklist file (`decklist.txt` or `input/<name>.txt`).
- Downloads card images into `image_cache/<type>/` and resizes them.
- Renders pages of 9 cards to an A4 PDF using the `pdf` package.

Optional features:
- Add cnc locator marks
- Draw background black square
- Change spaceing between cards
- Print two sided cards
- Add custom backside
- Handles custom cards(local images)
- Handles composit cards( nonstandar front/back)
