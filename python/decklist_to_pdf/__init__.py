"""
Decklist to PDF Package

A tool for converting Magic: The Gathering decklists to printable PDFs.
"""
from .models import (
    Config,
    CardSide,
    DecklistEntry,
    LayoutConstants,
    GAMMA_THRESHOLD,
    MAX_GAMMA,
    BORDER_SAMPLE_OFFSET,
    RETRY_COUNT,
    RATE_LIMIT_DELAY,
    CARD_WIDTH_MM,
    CARD_HEIGHT_MM,
    PAGE_WIDTH_MM,
    PAGE_HEIGHT_MM,
)
from .config import load_config, write_config
from .card_data import fetch_bulk_json, load_card_dictionary, card_data_lookup, read_decklist
from .image_processor import ImageProcessor
from .page_renderer import generate_layout_constants, render_page, render_all_pages
from .pdf_generator import merge_pages

__version__ = '0.2.0'
__all__ = [
    # Models
    'Config',
    'CardSide',
    'DecklistEntry',
    'LayoutConstants',
    # Config
    'load_config',
    'write_config',
    # Card data
    'fetch_bulk_json',
    'load_card_dictionary',
    'card_data_lookup',
    'read_decklist',
    # Image processing
    'ImageProcessor',
    # Page rendering
    'generate_layout_constants',
    'render_page',
    'render_all_pages',
    # PDF generation
    'merge_pages',
]

