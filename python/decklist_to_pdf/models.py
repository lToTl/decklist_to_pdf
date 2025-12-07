"""
Decklist to PDF - Data Models

Dataclasses for configuration, card data, and layout constants.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    """Configuration settings for the PDF generator."""
    decklist_path: str = 'decklist.txt'
    two_sided: bool = False
    split_double_faced: bool = False
    custom_backside: bool = False
    backside: str = 'back.png'
    pdf_path: str = 'output.pdf'
    image_type: str = 'png'
    spacing: int = 0
    mode: str = 'default'
    gamma_correction: bool = True
    reference_points: bool = True
    background_box: bool = True
    stagger: bool = True
    x_axis_offset: float = 0.75
    user_agent: str = 'decklist_to_pdf/0.1'
    accept: str = 'application/json;q=0.9,*/*;q=0.8'
    worker_threads: int = 4
    dpi: int = 600
    bulk_json_path: str = ''


@dataclass
class CardSide:
    """Represents one side of a card."""
    name: str
    key: str
    image_uris: dict = field(default_factory=dict)
    custom: bool = False
    two_sided: bool = False


@dataclass
class DecklistEntry:
    """A single entry in the decklist (may have multiple sides)."""
    sides: list[CardSide] = field(default_factory=list)


@dataclass
class LayoutConstants:
    """Pre-calculated layout constants for page rendering."""
    # Card dimensions in pixels
    card_width_px: int = 0
    card_height_px: int = 0
    
    # Page dimensions in pixels
    page_width_px: int = 0
    page_height_px: int = 0
    
    # Background box coordinates
    bg_box: tuple[float, float, float, float] = (0, 0, 0, 0)
    
    # Marker rectangles for reference points
    marker_rects: list = field(default_factory=list)
    
    # Card positions on page [row][col] = (x, y)
    card_positions_px: list = field(default_factory=list)
    
    # Image format (jpg or png)
    image_format: str = 'png'
    
    # DPI setting
    dpi: int = 600
    
    # img2pdf layout function
    a4_layout: Optional[object] = None
    
    # Deck info
    deck_size: int = 0
    total_pages: int = 0


# Image processing constants
GAMMA_THRESHOLD = 3  # Target brightness for black borders
MAX_GAMMA = 100  # Maximum allowed border brightness (skip if brighter)
BORDER_SAMPLE_OFFSET = 0.02  # Sample 2% from bottom edge
RETRY_COUNT = 3  # Number of retries for image operations
RATE_LIMIT_DELAY = 0.1  # Seconds between API calls

# Card dimensions in mm (MTG standard)
CARD_WIDTH_MM = 63
CARD_HEIGHT_MM = 88

# A4 page dimensions in mm
PAGE_WIDTH_MM = 210
PAGE_HEIGHT_MM = 297

# Layout settings
BG_BOX_MARGIN_MM = 2
CARDS_PER_PAGE = 9
GRID_ROWS = 3
GRID_COLS = 3
