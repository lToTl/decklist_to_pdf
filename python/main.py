#!/usr/bin/env python3
"""
Decklist to PDF - Main Entry Point

Converts Magic: The Gathering decklists into printable PDF files.
"""
import logging
import os
from time import perf_counter

from decklist_to_pdf.config import load_config, write_config
from decklist_to_pdf.card_data import fetch_bulk_json, load_card_dictionary, read_decklist
from decklist_to_pdf.image_processor import ImageProcessor
from decklist_to_pdf.page_renderer import generate_layout_constants, render_all_pages
from decklist_to_pdf.pdf_generator import merge_pages


# Sample decklist for first-time setup
SAMPLE_DECKLIST = """# Sample decklist - one card per line
# Format: copies Name (SET) collector_number
1 Lightning Bolt (M11) 149
1 Counterspell (MH2) 267
1 Sol Ring (C21) 263
1 Birds of Paradise (M12) 165
"""


def setup_directories() -> None:
    """Create all required directories and sample files for first-time setup."""
    # Main directories
    directories = [
        'scryfall_bulk_json',
        'cardbacks',
        'custom_cards', 
        'output',
        'input',
    ]
    
    # Image cache subdirectories
    image_types = ['small', 'normal', 'large', 'png', 'art_crop', 'border_crop']
    for img_type in image_types:
        directories.append(f'image_cache/{img_type}')
    
    # Create directories
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logging.info(f"Created directory: {directory}")
    
    # Create sample decklist if none exists
    if not os.listdir('input'):
        sample_path = 'input/decklist.txt'
        with open(sample_path, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_DECKLIST)
        logging.info(f"Created sample decklist: {sample_path}")


def main():
    """Main entry point for the decklist to PDF converter."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    full_start_time = perf_counter()
    logging.info("Starting decklist_to_pdf script")
    
    # Setup directories on first run
    setup_directories()
    
    # Load configuration
    config = load_config()
    
    # Fetch bulk JSON (prompts user)
    config.bulk_json_path = fetch_bulk_json(config, ask=False)
    write_config(config, ['bulk_json_path'])
    config.bulk_json_path = fetch_bulk_json(config, ask=True)
    write_config(config, ['bulk_json_path'])
    
    # Load Scryfall card data
    load_start = perf_counter()
    logging.info(f"Loading Scryfall bulk json from {config.bulk_json_path}")
    card_data = load_card_dictionary(config)
    logging.info(f"Loaded in {perf_counter() - load_start:.2f} seconds")
    
    # Generate layout constants
    constants = generate_layout_constants(config)
    
    # Get decklist name from user
    decklist_name = input(f"Enter decklist name (default: {config.decklist_path}): ").strip()
    
    if decklist_name:
        config.decklist_path = f"input/{decklist_name}.txt"
        write_config(config, ['decklist_path'])
    else:
        # Extract name from default path
        decklist_name = config.decklist_path.split('/')[-1].split('.')[0]
    
    # Read decklist
    logging.info(f"Reading decklist from {config.decklist_path}")
    decklist = read_decklist(config.decklist_path, card_data, config)
    logging.info(f"Found {len(decklist)} cards to print")
    
    # Update constants with deck info
    constants.deck_size = len(decklist)
    constants.total_pages = (len(decklist) + 8) // 9  # Ceiling division by 9
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    # Create PDF
    logging.info("Creating PDF")
    pdf_start = perf_counter()
    
    # Create image processor and cache images
    logging.info("Loading images into cache...")
    processor = ImageProcessor(
        config,
        constants.card_width_px,
        constants.card_height_px,
        constants.image_format
    )
    image_cache = processor.create_cache(decklist)
    
    # Render all pages
    pages = render_all_pages(decklist, image_cache, constants, config)
    
    # Merge pages into final PDF
    merge_start = perf_counter()
    logging.info("Merging pages into PDF")
    output_path = merge_pages(pages, config, constants, decklist_name)
    logging.info(f"PDF merged in {(perf_counter() - merge_start) * 1000:.0f} milliseconds")
    
    # Summary
    pdf_end = perf_counter()
    logging.info(f"PDF made in {pdf_end - pdf_start:.2f} seconds")
    logging.info(f"Finished in {perf_counter() - full_start_time:.2f} seconds")
    logging.info(f"Output: {output_path}")


if __name__ == '__main__':
    main()
