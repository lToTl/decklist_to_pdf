"""
Decklist to PDF - PDF Generation

Handles merging rendered pages into final PDF output.
"""
import io
import logging

from PyPDF2 import PdfMerger

from .models import Config, LayoutConstants


# Page ordering patterns for different printing modes
PAGE_PATTERNS = {
    'two_sided_stagger': [[0, 0], [1, 0], [0, 1], [1, 1]],  # F1, F2, B1, B2
    'two_sided_normal': [[0, 0], [0, 1], [1, 0], [1, 1]],   # F1, B1, F2, B2
    'one_sided': [[0, 0], [1, 0]],                          # F1, F2
}


def merge_pages(
    pages: dict[str, io.BytesIO],
    config: Config,
    constants: LayoutConstants,
    output_name: str
) -> str:
    """
    Merge rendered page buffers into a single PDF file.
    
    Args:
        pages: Dictionary mapping "page_index,side" to PDF BytesIO buffers
        config: Configuration object
        constants: Layout constants
        output_name: Name for the output file (without extension)
        
    Returns:
        Path to the generated PDF file
    """
    merger = PdfMerger()
    output_path = f"output/{output_name}.pdf"
    
    logging.info(f"Merging {len(pages)} page images into {output_name} PDF...")
    
    # Determine page ordering pattern
    if config.two_sided and config.stagger:
        pattern = PAGE_PATTERNS['two_sided_stagger']
    elif config.two_sided:
        pattern = PAGE_PATTERNS['two_sided_normal']
    else:
        pattern = PAGE_PATTERNS['one_sided']
    
    # Add pages in correct order
    page_index = 0
    while page_index < constants.total_pages:
        for offset in pattern:
            page_num = page_index + offset[0]
            side = offset[1]
            
            # Skip if page doesn't exist
            if page_num >= constants.total_pages:
                continue
            
            key = f"{page_num},{side}"
            if key in pages:
                merger.append(pages[key])
        
        page_index += 2
    
    # Write output file
    try:
        with open(output_path, "wb") as f:
            merger.write(f)
        logging.info(f"PDF created successfully at {output_path}")
        return output_path
        
    except Exception as e:
        logging.error(f"Error merging pages: {e}")
        raise
    finally:
        merger.close()
