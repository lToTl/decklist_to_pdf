from concurrent.futures import ThreadPoolExecutor
from time import sleep
from urllib.request import urlretrieve
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image
import requests
import logging
import json
import os


def load_card_dictionary(filepath):
    """
    Reads a JSON file containing card data and creates a dictionary.

    Args:
        filepath: The path to the JSON file.

    Returns:
        A dictionary where the keys are "set-collector_number" and the values
        are the corresponding card objects.  Returns an empty dictionary
        if the file doesn't exist or if there's a JSON decoding error.
    """
    card_dict = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as bulk_json:
            data = json.load(bulk_json)
            for card in data:
                if 'set' not in card or 'collector_number' not in card:
                    print(f"Warning: Skipping card due to missing 'set' or 'collector_number': {card.get('id', 'Unknown ID')}")
                    continue
                key = f"{card['set']}-{card['collector_number']}"
                card_dict[key] = card
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")
        return {}
    except Exception as e:
        print(f"Unexpected error occurred {e}")
        return {}

    logging.info(f"Loaded {len(card_dict)} cards from {filepath}")
    return card_dict

# TODO: double sided format
def read_decklist(filepath, backside):
    decklist = []
    with open(filepath, 'r', encoding='utf-8') as decklist_file:
        for decklist_line in decklist_file:
            copies = int(decklist_line[:decklist_line.index(" ")])
            name = decklist_line[decklist_line.index(" ") + 1:decklist_line.index("(") - 1]
            set_symbol = decklist_line[decklist_line.index("(") + 1:decklist_line.index(")")].lower()
            set_number = decklist_line[len(decklist_line) - decklist_line[::-1].index(" "):-1]
            decklist.append((copies, name, set_symbol, set_number))
    return decklist

def fetch_bulk_json():
    response = requests.get('https://api.scryfall.com/bulk-data/default-cards')
    response.raise_for_status()
    json_response = response.json()
    bulk_json_uri = json_response['download_uri']
    local_filename = f"scryfall_bulk_json/{bulk_json_uri.split('/')[-1]}"
    urlretrieve(bulk_json_uri, local_filename)
    return local_filename



def fetch_image(image_url,  destination):
    img_data = requests.get(image_url).content
    with open(destination, 'wb') as image_file:
        image_file.write(img_data)

def create_image_cache(image_type: str, card_data: dict, decklist: list) -> None:
    match image_type:
        case 'small'|'normal'|'large'|'art_crop'|'border_crop':
            image_format = 'jpg'
        case 'png':
            image_format = 'png'
        case _:
            logging.error(f"Unknown image type {image_type}")
            raise Exception(f"Unknown image type {image_type}")

    os.makedirs("image_cache/" + image_type, exist_ok=True)
    counter = 0
    with ThreadPoolExecutor(max_workers=12) as executor:
        for decklist_line in decklist:
            name = decklist_line[1]
            set_symbol = decklist_line[2]
            set_number = decklist_line[3]
            if not (os.path.exists(f"image_cache/{image_type}/{set_symbol}-{set_number}.{image_format}") or
                    os.path.exists(f"image_cache/{image_type}/{set_symbol}-{set_number}_A.{image_format}")):

                layout = card_data[f"{set_symbol}-{set_number}"]['layout']

                if layout == "normal" or layout == "token" or layout == "split" or layout == "flip":
                    logging.info(f"Downloading {name} -> {set_symbol}-{set_number}.{image_format}")
                    image_uri = card_data[f"{set_symbol}-{set_number}"]['image_uris'][image_type]
                    destination = f"image_cache/{image_type}/{set_symbol}-{set_number}.{image_format}"
                    executor.submit(fetch_image, image_uri, destination)
                    counter += 1

                if layout == "transform" or layout == "modal_dfc":
                    logging.info(logging.info(f"Downloading {name} -> {set_symbol}-{set_number}_A.{image_format}"))
                    image_uri = card_data[f"{set_symbol}-{set_number}"]['card_faces'][0]['image_uris'][image_type]
                    destination = f"image_cache/{image_type}/{set_symbol}-{set_number}_A.{image_format}"
                    executor.submit(fetch_image, image_uri, destination)
                    counter += 1

                    logging.info(logging.info(f"Downloading {name} -> {set_symbol}-{set_number}_B.{image_format}"))
                    image_uri = card_data[f"{set_symbol}-{set_number}"]['card_faces'][1]['image_uris'][image_type]
                    destination = f"image_cache/{image_type}/{set_symbol}-{set_number}_B.{image_format}"
                    executor.submit(fetch_image, image_uri, destination)
                    counter += 1
                sleep(0.1)
    logging.info(f"Downloaded {counter} new images")

# TODO: draw_reference_points
def draw_reference_points(canvas):
    pass

# TODO: rewrite card selection from listing image folder to respecting decklist 'copies' parameter
# TODO: double sided card placement
# TODO: x_axis_offset
# TODO: Bleed edge mode
def create_grid_pdf(image_folder, output_filename, conf):
    """
    Generates a PDF with A4 pages, each containing a 3x3 grid of rectangles.
    Each rectangle displays an image from the specified folder.

    Args:
        :param image_folder: The path to the folder containing the images.
        :param output_filename: The name of the PDF file to be created.
        :param conf: configuration dictionary.
    """

    # --- Constants (in mm) ---
    rectangle_width = 63
    rectangle_height = 88
    spacing = 2
    grid_width = 3 * rectangle_width + 2 * spacing
    grid_height = 3 * rectangle_height + 2 * spacing

    # --- A4 Page Dimensions (in mm) ---
    page_width, page_height = A4
    page_width_mm = page_width / mm
    page_height_mm = page_height / mm

    # --- Calculate Grid Offsets ---
    grid_x_offset = (page_width_mm - grid_width) / 2
    grid_y_offset = (page_height_mm - grid_height) / 2


    # --- Get Image Files ---
    image_files = sorted([f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))])  # Add more extensions if needed

    if not image_files:
        print("No images found in the specified folder.")
        return

    # --- Create PDF ---
    c = canvas.Canvas(output_filename, pagesize=A4)

    image_index = 0
    if conf['reference_points']:
        draw_reference_points(c)

    while image_index < len(image_files):
        # --- Black Background Rectangle ---
        c.setFillColorRGB(0, 0, 0)  # Black
        c.rect(grid_x_offset * mm, grid_y_offset * mm, grid_width * mm, grid_height * mm, fill=1)


        # --- Draw Grid of Rectangles and Images ---
        for row in range(3):
            for col in range(3):
                if image_index < len(image_files):
                    image_path = os.path.join(image_folder, image_files[image_index])

                    # Calculate rectangle position
                    x = grid_x_offset + col * (rectangle_width + spacing)
                    y = page_height_mm - (grid_y_offset + (row + 1) * (rectangle_height + spacing) - spacing) # Inverted y-axis

                    # Draw Rectangle (optional, for debugging/border)
                    #c.setFillColorRGB(1, 1, 1) # White
                    #c.rect(x * mm, y * mm, rectangle_width * mm, rectangle_height * mm, stroke=1, fill=0)

                    # --- Image Placement ---
                    try:
                        img = Image.open(image_path)
                        img_width, img_height = img.size

                        # Calculate scaling factor (fit image within rectangle)
                        scale_x = (rectangle_width * mm) / img_width
                        scale_y = (rectangle_height * mm) / img_height
                        scale = min(scale_x, scale_y)

                        # Calculate centered image position
                        draw_width = img_width * scale
                        draw_height = img_height * scale
                        draw_x = x * mm + (rectangle_width * mm - draw_width) / 2
                        draw_y = y * mm + (rectangle_height * mm - draw_height) / 2

                        c.drawImage(image_path, draw_x, draw_y, width=draw_width, height=draw_height, mask='auto')
                    except Exception as e:
                        print(f"Error processing image {image_path}: {e}") # Handle image loading errors

                    image_index += 1

        c.showPage()  # Move to the next page
    c.save()
    print(f"PDF created: {output_filename}")


def write_config(conf):
    logging.info("Creating config file...")
    with open('decklist_to_pdf.ini', 'w') as config_file:
        config_file.write(f"""# relative path to scryfall default-cards bulk json, leave empty to fetch fresh one from scryfall (~465MB)
bulk_json_path:{conf['bulk_json_path']}

# relative path to decklist listing unique cards one per line in of the formats:
# copies name (SET) collector_number
# copies name (SET) collector_number | backside.jpg/*.png
# copies name (SET) collector_number | (SET) collector_number
decklist_path:{conf['decklist_path']}

# default backside image
backside:{conf['backside']}

# relative export path for pdf
pdf_path:{conf['pdf_path']}

# possible image types are small / normal / large / png / art_crop / border_crop
image_type:{conf['image_type']}

# default - for regular black border cards. Image size is 63x88 mm with 2 mm black spacing between cards
# bleed edge - for full art cards. Image size is 65x90.79 mm with no spacing between cards
mode:{conf['mode']}

# toggle reference point True/False
reference_points:{conf['reference_points']}

# move everything on the x_axis
x_axis_offset:{conf['x_axis_offset']}""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Default configuration values
    config = {
        'bulk_json_path' : 'scryfall_bulk_json/default-cards-20250220101107.json',
        'decklist_path' : 'decklist.txt',
        'backside': 'back.jpg',
        'pdf_path' : 'output.pdf',
        'image_type' : 'png',
        'mode' : 'default',
        'reference_points' : True,
        'x_axis_offset' : 0
    }


    if not os.path.exists('decklist_to_pdf.ini'):
        write_config(config)

    logging.info("Loading configuration from decklist_to_pdf.ini")
    with open("decklist_to_pdf.ini", "r") as f:
        for line in f:
            if line[0] == '#':
                continue
            parts = line.strip().split(':')
            match parts[0]:
                case 'bulk_json_path':
                    config['bulk_json_path'] = parts[1]
                case 'decklist_path':
                    config['decklist_path'] = parts[1]
                case 'backside':
                    config['backside'] = parts[1]
                case 'pdf_path':
                    config['pdf_path'] = parts[1]
                case 'image_type':
                    config['image_type'] = parts[1]
                case 'mode':
                    config['mode'] = parts[1]
                case 'reference_points':
                    config['reference_points'] = parts[1]
                case 'x_axis_offset':
                    config['x_axis_offset'] = parts[1]

    if not os.path.exists(config['bulk_json_path']):
        config['bulk_json_path'] = fetch_bulk_json()
        write_config(config)

    logging.info(f"Loading Scryfall bulk json to dictionary from {config['bulk_json_path']}")
    card_dictionary = load_card_dictionary(config['bulk_json_path'])

    logging.info(f"Reading decklist from {config['decklist_path']}")
    deck_data = read_decklist(config['decklist_path'], config['backside'])
    logging.info(f"Found {len(deck_data)} unique cards in decklist")

    logging.info("Checking image cache")
    create_image_cache(image_type=config['image_type'], card_data=card_dictionary, decklist=deck_data)

    logging.info("Creating PDF")

    create_grid_pdf("image_cache/png", "test.pdf", config['pdf_path'])

