"""
Decklist to PDF - Card Data Management

Handles Scryfall bulk data loading, parsing, and card lookups.
"""
import logging
import os
import urllib.request
from urllib.request import Request

import orjson
import requests

from .models import Config, CardSide, DecklistEntry


def fetch_bulk_json(config: Config, ask: bool = True) -> str:
    """
    Download or locate Scryfall bulk JSON file.
    
    Args:
        config: Configuration object
        ask: Whether to prompt user for download confirmation
        
    Returns:
        Path to the bulk JSON file
    """
    if ask:
        response = input("Do you want to update Scryfall bulk JSON? (y/n): ").strip().lower()
        if response != 'y':
            logging.info("Skipping Scryfall bulk JSON download.")
            return config.bulk_json_path
    
    headers = {
        'User-Agent': config.user_agent,
        'Accept': config.accept
    }
    
    response = requests.get('https://api.scryfall.com/bulk-data/default-cards', headers=headers)
    response.raise_for_status()
    
    json_response = response.json()
    bulk_json_uri = json_response['download_uri']
    local_filename = f"scryfall_bulk_json/{bulk_json_uri.split('/')[-1]}"
    
    # Ensure directory exists
    os.makedirs('scryfall_bulk_json', exist_ok=True)
    
    if os.path.exists(local_filename):
        return local_filename
    
    logging.info('Downloading new Scryfall bulk data...')
    request = Request(bulk_json_uri, headers=headers)
    with urllib.request.urlopen(request) as http_response, open(local_filename, 'wb') as out_file:
        out_file.write(http_response.read())
    
    return local_filename


def load_card_dictionary(config: Config) -> dict:
    """
    Load and parse Scryfall bulk JSON into a card dictionary.
    
    Args:
        config: Configuration object with bulk_json_path
        
    Returns:
        Dictionary mapping card keys to card data
    """
    filepath = config.bulk_json_path
    parts = filepath.split('/')
    parsed_path = f"{parts[0]}/parsed_{parts[-1]}"
    
    print(parsed_path)
    
    # Try loading pre-parsed data first
    if os.path.exists(parsed_path):
        return _load_parsed_json(parsed_path)
    
    # Parse raw bulk JSON
    return _parse_bulk_json(filepath, parsed_path)


def _load_parsed_json(filepath: str) -> dict:
    """Load pre-parsed card dictionary from JSON file."""
    try:
        print("Loading parsed JSON...")
        with open(filepath, 'r', encoding='utf-8') as f:
            return orjson.loads(f.read())
    except orjson.JSONDecodeError as e:
        logging.error(f"Invalid JSON format in {filepath}")
        raise
    except MemoryError as e:
        logging.error(f"Out of memory while reading {filepath}")
        raise
    except FileNotFoundError:
        logging.error(f"File not found at {filepath}")
        raise


def _parse_bulk_json(filepath: str, parsed_path: str) -> dict:
    """Parse raw Scryfall bulk JSON and cache the result."""
    card_dict = {}
    
    print(f"Loading unparsed bulk JSON from {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            print("Parsing JSON...")
            data = orjson.loads(f.read())
            
            for card in data:
                key = f"{card['set'].lower()}-{card['collector_number']}"
                
                if card['layout'] in {'transform', 'modal_dfc', 'double_faced_token', 'reversible_card'}:
                    _parse_double_faced_card(card, key, card_dict)
                elif card['layout'] in _SINGLE_FACED_LAYOUTS:
                    _parse_single_faced_card(card, key, card_dict)
                elif card['layout'] != 'art_series':
                    print(f"Unknown layout {card['layout']} for card {card['name']}")
            
            # Cache parsed data
            with open(parsed_path, 'w', encoding='utf-8') as out:
                out.write(orjson.dumps(card_dict).decode())
            
            print(f"Parsed {len(card_dict)} cards from {filepath}")
            
    except orjson.JSONDecodeError:
        logging.error(f"Invalid JSON format in {filepath}")
        raise
    except MemoryError as e:
        logging.error(f"Out of memory while reading {filepath}. {len(card_dict)} cards loaded.")
        raise
    except FileNotFoundError:
        logging.error(f"File not found at {filepath}")
        raise
    
    logging.info(f"Loaded {len(card_dict)} cards from {filepath}")
    return card_dict


_SINGLE_FACED_LAYOUTS = {
    'normal', 'token', 'split', 'layout', 'flip', 'mutate', 'adventure',
    'emblem', 'scheme', 'vanguard', 'planar', 'phenomenon', 'saga',
    'augment', 'leveler', 'prototype', 'host', 'case', 'class', 'meld'
}


def _parse_double_faced_card(card: dict, key: str, card_dict: dict) -> None:
    """Parse a double-faced card into the dictionary."""
    side = 'A'
    for face in card['card_faces']:
        card_dict[f"{key}_{side}"] = {
            'name': face['name'],
            'image_uris': face['image_uris'],
            'layout': card['layout'],
            'two_sided': True,
            'other_face': f"{key}_{'B' if side == 'A' else 'A'}",
            'border_color': card['border_color']
        }
        side = 'B'
    
    card_dict[key] = {
        'name': card['name'],
        'set': card['set'],
        'collector_number': card['collector_number'],
        'layout': card['layout'],
        'two_sided': True,
        'faces': [card_dict[f"{key}_A"], card_dict[f"{key}_B"]],
        'border_color': card['border_color']
    }


def _parse_single_faced_card(card: dict, key: str, card_dict: dict) -> None:
    """Parse a single-faced card into the dictionary."""
    card_dict[key] = {
        'name': card['name'],
        'set': card['set'],
        'collector_number': card['collector_number'],
        'image_uris': card['image_uris'],
        'layout': card['layout'],
        'two_sided': False,
        'border_color': card['border_color']
    }


def card_data_lookup(decklist_line: str, card_data: dict) -> dict:
    """
    Look up card data from a decklist line.
    
    Args:
        decklist_line: Line from decklist in format "Name (SET) number"
        card_data: Card dictionary from load_card_dictionary
        
    Returns:
        Dictionary with card info including image_uris
        
    Raises:
        KeyError: If card not found in data
    """
    set_symbol = decklist_line[decklist_line.index("(") + 1:decklist_line.index(")")].lower()
    set_number = decklist_line[len(decklist_line) - decklist_line[::-1].index(" "):].strip()
    key = f"{set_symbol}-{set_number}"
    
    # Handle forced side markers
    force_side = 0
    if decklist_line.startswith("!!"):
        force_side = 2
        decklist_line = decklist_line[2:].strip()
    elif decklist_line.startswith("!"):
        force_side = 1
        decklist_line = decklist_line[1:].strip()
    
    try:
        data = card_data[key]
    except KeyError:
        raise KeyError(
            f"Card {decklist_line} not found in card data. "
            "Please check the decklist format or the card data."
        )
    
    return {
        'name': decklist_line[:decklist_line.index("(") - 1],
        'key': key if force_side == 0 else f"{key}_{'A' if force_side == 1 else 'B'}",
        'black_border': data['border_color'] == "black",
        'force_side': force_side,
        'sides': data.get('faces') if data['two_sided'] and force_side == 0 else None,
        'image_uris': data['image_uris'] if 'image_uris' in data else data['faces'][force_side - 1]['image_uris']
    }


def read_decklist(filepath: str, card_data: dict, config: Config) -> list[dict]:
    """
    Read and parse a decklist file.
    
    Args:
        filepath: Path to the decklist file
        card_data: Card dictionary from load_card_dictionary
        config: Configuration object
        
    Returns:
        List of decklist entries
    """
    decklist = []
    line_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line_count += 1
                line = line.strip()
                
                # Skip comments and empty lines
                if line.startswith("#") or line == "":
                    continue
                
                copies = int(line[:line.index(" ")])
                card_line = line[line.index(" ") + 1:].strip()
                
                if "|" in card_line:
                    # Composite card (multiple faces)
                    entry = _parse_composite_card(card_line, copies, card_data)
                elif card_line.startswith("*"):
                    # Custom card
                    entry = _parse_custom_card(card_line, copies)
                else:
                    # Normal card
                    entry = _parse_normal_card(card_line, copies, card_data, config)
                
                _add_to_decklist(entry, decklist, config)
                
    except FileNotFoundError:
        logging.error(f"Decklist file {filepath} not found.")
        raise
    except Exception as e:
        logging.error(f"Error reading decklist file {filepath} on line {line_count}: {e}")
        raise
    
    return decklist


def _parse_composite_card(card_line: str, copies: int, card_data: dict) -> dict:
    """Parse a composite card with multiple faces."""
    faces = []
    for face in card_line.split("||"):
        face = face.strip()
        if face.startswith("*"):
            # Custom face
            name = face[1:]
            faces.append({'name': name, 'key': name, 'black_border': False, 'custom': True})
        else:
            faces.append(card_data_lookup(face, card_data))
    
    return {
        'copies': copies,
        'sides': faces,
        'two_sided': True,
        'composite': True
    }


def _parse_custom_card(card_line: str, copies: int) -> dict:
    """Parse a custom card entry."""
    name = card_line[card_line.index("*") + 1:].strip()
    return {
        'name': name,
        'key': name,
        'two_sided': False,
        'black_border': False,
        'custom': True,
        'composite': False,
        'copies': copies
    }


def _parse_normal_card(card_line: str, copies: int, card_data: dict, config: Config) -> dict:
    """Parse a normal card entry."""
    entry = card_data_lookup(card_line, card_data)
    entry.update({
        'copies': copies,
        'composite': False,
        'two_sided': False,
        'custom': False
    })
    return entry


def _add_to_decklist(card_data: dict, decklist: list, config: Config) -> None:
    """
    Add card data to the decklist with proper handling of sides.
    
    Handles various scenarios:
    - Single-faced cards
    - Double-faced cards (transform, modal_dfc, etc.)
    - Custom backsides
    - Split double-faced mode (print both faces as separate cards)
    """
    copies = card_data.pop('copies', 1)
    data_to_add = []
    
    has_sides = 'sides' in card_data and card_data['sides'] is not None
    is_composite = card_data.get('composite', False)
    is_custom = card_data.get('custom', False)
    
    if has_sides and not is_composite and not is_custom:
        # Double-faced card from Scryfall
        sides = card_data['sides']
        
        if config.split_double_faced and not config.two_sided:
            # Print each face as a separate single-sided card
            for i, side in enumerate(sides):
                suffix = '_A' if i == 0 else '_B'
                side_entry = {
                    'key': f"{card_data['key']}{suffix}",
                    'name': side.get('name', card_data.get('name', '')),
                    'image_uris': side.get('image_uris', {}),
                    'custom': False,
                    'two_sided': False,
                }
                data_to_add.append({'sides': [side_entry]})
        
        elif config.two_sided and config.custom_backside:
            # Two-sided printing with custom back
            for i, side in enumerate(sides):
                suffix = '_A' if i == 0 else '_B'
                side_entry = {
                    'key': f"{card_data['key']}{suffix}",
                    'name': side.get('name', ''),
                    'image_uris': side.get('image_uris', {}),
                    'custom': False,
                    'two_sided': False,
                }
                data_to_add.append({'sides': [side_entry, {'key': 'back'}]})
        
        elif config.two_sided:
            # Normal two-sided printing (front/back aligned)
            front = sides[0].copy()
            back = sides[1].copy() if len(sides) > 1 else {'key': 'back'}
            front.update({'key': f"{card_data['key']}_A", 'custom': False, 'two_sided': True})
            back.update({'key': f"{card_data['key']}_B", 'custom': False, 'two_sided': True})
            data_to_add.append({'sides': [front, back]})
        
        else:
            # Single-sided printing - only print front face
            front = sides[0].copy()
            front.update({'key': f"{card_data['key']}_A", 'custom': False, 'two_sided': False})
            data_to_add.append({'sides': [front]})
    
    elif has_sides and is_composite:
        # Composite card (user-defined front/back)
        for side in card_data['sides']:
            side.update({'custom': side.get('custom', False)})
        data_to_add.append({'sides': card_data['sides']})
    
    elif config.custom_backside and not is_composite:
        # Single-faced card with custom backside
        card_data['custom'] = card_data.get('custom', False)
        data_to_add.append({'sides': [card_data, {'key': 'back'}]})
    
    else:
        # Single-faced card, single-sided printing
        card_data['custom'] = card_data.get('custom', False)
        data_to_add.append({'sides': [card_data]})
    
    # Add copies to decklist
    for _ in range(copies):
        decklist.extend(data_to_add)

