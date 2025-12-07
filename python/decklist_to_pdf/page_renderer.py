"""
Decklist to PDF - Page Rendering

Handles page layout calculation and rendering cards onto pages.
"""
import io
import logging
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

import img2pdf
from PIL import Image, ImageDraw

from .models import (
    Config,
    LayoutConstants,
    CARD_WIDTH_MM,
    CARD_HEIGHT_MM,
    PAGE_WIDTH_MM,
    PAGE_HEIGHT_MM,
    BG_BOX_MARGIN_MM,
    GRID_ROWS,
    GRID_COLS,
)


def generate_layout_constants(config: Config) -> LayoutConstants:
    """
    Calculate all layout constants based on configuration.
    
    Args:
        config: Configuration object
        
    Returns:
        LayoutConstants with pre-calculated pixel positions
    """
    dpi = config.dpi
    
    # Convert mm to pixels
    def mm_to_px(val_mm: float) -> int:
        return int(val_mm * dpi / 25.4)
    
    # Card dimensions in pixels
    card_width_px = mm_to_px(CARD_WIDTH_MM)
    card_height_px = mm_to_px(CARD_HEIGHT_MM)
    spacing_px = mm_to_px(config.spacing)
    bg_box_margin_px = mm_to_px(BG_BOX_MARGIN_MM)
    
    # Page dimensions in pixels
    page_width_px = mm_to_px(PAGE_WIDTH_MM)
    page_height_px = mm_to_px(PAGE_HEIGHT_MM)
    
    # Grid dimensions
    grid_width_px = GRID_COLS * card_width_px + (GRID_COLS - 1) * spacing_px
    grid_height_px = GRID_ROWS * card_height_px + (GRID_ROWS - 1) * spacing_px
    
    # X-axis offset
    x_axis_offset_px = mm_to_px(float(config.x_axis_offset))
    
    # Grid offsets (centering)
    grid_x_offset_px = ((page_width_px - grid_width_px) / 2) + x_axis_offset_px
    grid_y_offset_px = (page_height_px - grid_height_px) / 2
    
    # Grid center
    grid_center_x_px = page_width_px / 2 + x_axis_offset_px
    grid_center_y_px = page_height_px / 2
    
    # Background box
    bg_box_width_px = card_width_px * GRID_COLS + bg_box_margin_px * 2
    bg_box_height_px = card_height_px * GRID_ROWS + bg_box_margin_px * 2
    bg_box_x = grid_x_offset_px - bg_box_margin_px
    bg_box_y = grid_y_offset_px - bg_box_margin_px
    bg_box = (bg_box_x, bg_box_y, bg_box_x + bg_box_width_px, bg_box_y + bg_box_height_px)
    
    # Reference marker rectangles
    marker_rects = _calculate_marker_rects(grid_center_x_px, grid_center_y_px, mm_to_px)
    
    # Card positions [row][col] = (x, y)
    card_positions_px = []
    for row in range(GRID_ROWS):
        row_positions = []
        for col in range(GRID_COLS):
            x = grid_x_offset_px + col * (card_width_px + spacing_px)
            # Y: 0,0 is top-left in PIL, so we flip the row order
            # Row 0 is at the top, row 2 is at the bottom
            y = grid_y_offset_px + row * (card_height_px + spacing_px)
            row_positions.append([int(x), int(y)])
        card_positions_px.append(row_positions)
    
    # img2pdf A4 layout
    a4_points = (img2pdf.mm_to_pt(PAGE_WIDTH_MM), img2pdf.mm_to_pt(PAGE_HEIGHT_MM))
    a4_layout = img2pdf.get_layout_fun(a4_points)
    
    # Determine image format
    image_type = config.image_type
    if image_type in {'small', 'normal', 'large', 'art_crop', 'border_crop'}:
        image_format = 'jpg'
    elif image_type == 'png':
        image_format = 'png'
    else:
        raise ValueError(f"Unknown image type: {image_type}")
    
    return LayoutConstants(
        card_width_px=card_width_px,
        card_height_px=card_height_px,
        page_width_px=page_width_px,
        page_height_px=page_height_px,
        bg_box=bg_box,
        marker_rects=marker_rects,
        card_positions_px=card_positions_px,
        image_format=image_format,
        dpi=dpi,
        a4_layout=a4_layout,
    )


def _calculate_marker_rects(center_x: float, center_y: float, mm_to_px) -> list:
    """Calculate reference marker rectangles for cutting guides."""
    marker_vectors = [[mm_to_px(2), mm_to_px(2)], [-mm_to_px(2), -mm_to_px(2)]]
    marker_iterations = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
    
    marker_rects = []
    for iteration in marker_iterations:
        for vector in marker_vectors:
            pos_x = center_x + mm_to_px(iteration[0] * 193 / 2)
            pos_y = center_y + mm_to_px(iteration[1] * 278 / 2)
            
            sorted_x = sorted([pos_x, pos_x + vector[0]])
            sorted_y = sorted([pos_y, pos_y + vector[1]])
            
            marker_rects.append([sorted_x[0], sorted_y[0], sorted_x[1], sorted_y[1]])
    
    return marker_rects


def render_page(
    page_index: int,
    side: int,
    decklist: list[dict],
    image_cache: dict[str, Image.Image],
    constants: LayoutConstants,
    config: Config,
    pages: dict[str, io.BytesIO]
) -> None:
    """
    Render a single page with up to 9 cards.
    
    Args:
        page_index: Index of the page (0-based)
        side: 0 for front, 1 for back
        decklist: List of decklist entries
        image_cache: Dictionary of cached card images
        constants: Layout constants
        config: Configuration object
        pages: Output dictionary for page buffers
    """
    card_index_start = page_index * 9
    deck_size = constants.deck_size
    
    if card_index_start >= deck_size:
        return
    
    # Create blank A4 page
    page_image = Image.new(
        'RGB',
        (constants.page_width_px, constants.page_height_px),
        color=(255, 255, 255)
    )
    draw = ImageDraw.Draw(page_image)
    
    # Draw background rectangle (if enabled)
    if config.background_box:
        draw.rectangle(constants.bg_box, fill=(0, 0, 0), width=0)
    
    # Place cards on page
    card_index = card_index_start
    placement_times = []
    
    for row_index in range(GRID_ROWS):
        for col_index in range(GRID_COLS):
            if card_index >= deck_size:
                break
            
            timer_start = perf_counter()
            card = decklist[card_index]
            
            # Get image from cache
            key = card['sides'][side]['key']
            img = image_cache.get(key)
            
            if img is None:
                logging.error(f"Image not found in cache for key: {key}")
                raise KeyError(f"Missing image: {key}")
            
            # For back side, flip column position for alignment
            x_index = 2 - col_index if side == 1 else col_index
            
            draw_x = constants.card_positions_px[row_index][x_index][0]
            draw_y = constants.card_positions_px[row_index][x_index][1]
            
            page_image.paste(img, (draw_x, draw_y))
            
            card_index += 1
            placement_times.append(perf_counter() - timer_start)
    
    # Draw reference points
    if config.reference_points:
        for rect in constants.marker_rects:
            draw.rectangle(rect, fill=(0, 0, 0), width=0)
    
    # Convert to PDF page
    side_name = 'front' if side == 0 else 'back'
    
    buffer_start = perf_counter()
    buffer = io.BytesIO()
    page_image.save(buffer, format='PNG')
    buffer.seek(0)
    logging.info(f"Buffered page {page_index} {side_name} in {(perf_counter() - buffer_start) * 1000:.0f}ms")
    
    pdf_start = perf_counter()
    pdf_bytes = img2pdf.convert(buffer, layout_fun=constants.a4_layout)
    if pdf_bytes is None:
        raise ValueError(f"img2pdf.convert returned None for page {page_index}, side {side}")
    
    pages[f"{page_index},{side}"] = io.BytesIO(pdf_bytes)
    logging.info(f"PDF for page {page_index} {side_name} in {(perf_counter() - pdf_start) * 1000:.0f}ms")


def render_all_pages(
    decklist: list[dict],
    image_cache: dict[str, Image.Image],
    constants: LayoutConstants,
    config: Config
) -> dict[str, io.BytesIO]:
    """
    Render all pages for the decklist.
    
    Args:
        decklist: List of decklist entries
        image_cache: Dictionary of cached card images
        constants: Layout constants
        config: Configuration object
        
    Returns:
        Dictionary mapping "page_index,side" to PDF BytesIO buffers
    """
    logging.info("Rendering pages as images...")
    pages: dict[str, io.BytesIO] = {}
    
    with ThreadPoolExecutor(max_workers=config.worker_threads) as executor:
        # Submit front pages
        for i in range(constants.total_pages):
            logging.info(f'Submitting render page {i} front')
            executor.submit(render_page, i, 0, decklist, image_cache, constants, config, pages)
        
        # Submit back pages if two-sided
        if config.two_sided:
            for i in range(constants.total_pages):
                logging.info(f'Submitting render page {i} back')
                executor.submit(render_page, i, 1, decklist, image_cache, constants, config, pages)
        
        executor.shutdown(wait=True)
    
    logging.info("Finished rendering pages as images.")
    return pages
