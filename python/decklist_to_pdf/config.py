"""
Decklist to PDF - Configuration Management

Handles loading and writing configuration from/to INI files.
"""
import logging
import os
from dataclasses import asdict, fields

from .models import Config


def load_config(config_path: str = 'decklist_to_pdf.ini') -> Config:
    """
    Load configuration from INI file, falling back to defaults.
    
    Args:
        config_path: Path to the INI file
        
    Returns:
        Config dataclass with loaded or default values
    """
    config = Config()
    
    if os.path.exists(config_path):
        logging.info(f"Loading configuration from {config_path}")
        config = _read_config(config_path, config)
    else:
        logging.info(f"{config_path} not found, using default configuration")
    
    return config


def _read_config(config_path: str, config: Config) -> Config:
    """
    Read configuration values from INI file.
    
    Args:
        config_path: Path to the INI file
        config: Config object with defaults
        
    Returns:
        Updated Config object
    """
    config_dict = asdict(config)
    valid_keys = set(config_dict.keys())
    found_keys = set()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Skip empty lines and comments
                if not line.strip() or line.lstrip().startswith('#'):
                    continue
                    
                parts = line.strip().split(':')
                if len(parts) < 2:
                    continue
                    
                key = parts[0].strip()
                value = ':'.join(parts[1:]).strip()  # Handle values containing ':'
                
                if key not in valid_keys:
                    continue
                    
                found_keys.add(key)
                config_dict[key] = _parse_value(value)
                
    except FileNotFoundError:
        logging.error(f"{config_path} inaccessible.")
        raise
    except PermissionError:
        logging.error(f"Permission denied reading {config_path}")
        raise
    
    # Write any missing config entries
    missing_keys = valid_keys - found_keys - {'bulk_json_path'}
    if missing_keys:
        logging.info(f"Writing missing configuration entries: {', '.join(missing_keys)}")
        write_config(Config(**config_dict), list(missing_keys), config_path)
    
    return Config(**config_dict)


def _parse_value(value: str):
    """
    Parse a string value to its appropriate type.
    
    Args:
        value: String value from config file
        
    Returns:
        Parsed value (bool, int, float, or str)
    """
    if value == 'True':
        return True
    if value == 'False':
        return False
    
    # Try integer
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value)
    except ValueError:
        pass
    
    return value


def write_config(config: Config, keys: list[str], config_path: str = 'decklist_to_pdf.ini') -> None:
    """
    Write or update configuration entries in INI file.
    
    Updates existing keys in place, appends new keys at the end.
    
    Args:
        config: Config object with current values
        keys: List of keys to write
        config_path: Path to the INI file
    """
    config_dict = asdict(config)
    
    config_comments = {
        'bulk_json_path': '# relative path to scryfall bulk json file',
        'decklist_path': '''# relative path to decklist listing unique cards one per line in of the formats:
# copies name (SET) collector_number
# copies name (SET) collector_number | backside.jpg/*.png
# copies name (SET) collector_number | (SET) collector_number''',
        'two_sided': '# two sided printing',
        'split_double_faced': '# print both faces of double-faced cards as separate cards (when two_sided is False)',
        'custom_backside': '# has custom backside',
        'backside': '# default backside image',
        'pdf_path': '# relative export path for pdf',
        'image_type': '# possible image types are small / normal / large / png / art_crop / border_crop',
        'spacing': '# spacing between cards in mm',
        'mode': '''# default - for regular black border cards. Image size is 63x88 mm with 2 mm black spacing between cards
# bleed edge - for full art cards. Image size is 65x90.79 mm with no spacing between cards''',
        'gamma_correction': '# gamma correction for images',
        'reference_points': '# toggle reference points True/False',
        'background_box': '# toggle black background box behind cards True/False',
        'stagger': '# stagger pages for faster 2 sided printing with slow printers (Front,Front,Back,Back)',
        'x_axis_offset': '# move everything on the x_axis',
        'user_agent': '# user agent for scryfall bulk json download',
        'accept': '# accept header for scryfall bulk json download',
        'worker_threads': '# number of threads to use for rendering pages and image processing',
        'dpi': '# pixel density for printing',
    }
    
    keys_to_write = set(keys) & set(config_dict.keys())
    if not keys_to_write:
        return
    
    # Read existing file content
    existing_lines = []
    existing_keys = set()
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as file:
            existing_lines = file.readlines()
        
        # Find which keys already exist in the file
        for line in existing_lines:
            if line.strip() and not line.lstrip().startswith('#'):
                parts = line.strip().split(':')
                if len(parts) >= 2:
                    existing_keys.add(parts[0].strip())
    
    # Update existing keys in place
    updated_lines = []
    for line in existing_lines:
        if line.strip() and not line.lstrip().startswith('#'):
            parts = line.strip().split(':')
            if len(parts) >= 2:
                key = parts[0].strip()
                if key in keys_to_write and key in existing_keys:
                    # Update this line with new value
                    updated_lines.append(f"{key}:{config_dict[key]}\n")
                    continue
        updated_lines.append(line)
    
    # Append new keys that don't exist yet
    new_keys = keys_to_write - existing_keys
    for key in new_keys:
        comment = config_comments.get(key, '')
        updated_lines.append(f"\n{comment}\n{key}:{config_dict[key]}\n")
    
    # Write back the file
    with open(config_path, 'w', encoding='utf-8') as file:
        file.writelines(updated_lines)
