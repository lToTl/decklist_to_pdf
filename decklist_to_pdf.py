import urllib.request
from concurrent.futures import ThreadPoolExecutor
from time import sleep, time
from urllib.request import urlretrieve, Request
# Removed reportlab imports: from reportlab.lib.pagesizes import A4
# Removed reportlab imports: from reportlab.pdfgen import canvas
# Removed reportlab imports: from reportlab.lib.units import mm,inch
# Removed reportlab imports: from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfMerger, PdfReader
from PIL import Image, ImageEnhance, ImageDraw
import time
import requests
import logging
import orjson
import os
import io
import re
import img2pdf # Added img2pdf
import glob # Added glob
import math # Added math for pixel calculations
#import gc


def load_card_dictionary(filepath) -> dict:

    card_dict = {}
    print(f'{filepath.split('/')[0]}/parsed_{filepath.split('/')[-1]}')
    if os.path.exists(f'{filepath.split('/')[0]}/parsed_{filepath.split('/')[-1]}'):
        try:
            with open(f'{filepath.split('/')[0]}/parsed_{filepath.split('/')[-1]}', 'r', encoding='utf-8') as bulk_json:
                print("Loading parsed JSON...")
                # Use ijson to parse the JSON file incrementally
                # This is more memory efficient for large files
                return orjson.loads(bulk_json.read())

        # crash the program if the file is not loaded correctly
        except orjson.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in {filepath}")
            raise e
        except MemoryError as e:
            print(f"Out of memory while reading {filepath}. {len(card_dict)} cards into the file. Error: {e}")
            raise e
        except FileNotFoundError as e:
            print(f"Error: File not found at {filepath}")
            raise e

    else:
        print("Loading unparsed bulk JSON...")
        try:
            print(f"Opening: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as bulk_json:
                print("Parsing JSON...")
                # Use ijson to parse the JSON file incrementally
                # This is more memory efficient for large files
                bulk_json.buffer
                data = orjson.loads(bulk_json.read())
                # Read the next chunk of data
                for card in data:
                    #print(f"Processing card: {card['name']}")
                    # Create a key using set and collector_number
                    key = f"{card['set'].lower()}-{card['collector_number']}"
                    # Add needed card data to the dictionary
                    if card['layout'] in {'transform', 'modal_dfc', 'double_faced_token','reversible_card'}:
                        side = 'A'
                        for face in card['card_faces']:
                            card_dict[f"{key}_{side}"] = {'name': face['name'],
                                        'image_uris': face['image_uris'],
                                        'layout': card['layout'],
                                        'two_sided': True,
                                        'other_face': f"{key}_{'B' if side == 'A' else 'A'}",
                                        'border_color': card['border_color']}
                            side = 'B'

                    elif card['layout'] in {
                        'normal',
                        'token',
                        'split',
                        'layout',
                        'flip',
                        'mutate',
                        'adventure',
                        'emblem',
                        'scheme',
                        'vanguard',
                        'planar',
                        'phenomenon',
                        'saga',
                        'augment',
                        'leveler',
                        'prototype',
                        'host',
                        'case',
                        'class',
                        'meld'
                        }:
                            card_dict[key] = {'name': card['name'],
                                    'set': card['set'],
                                    'collector_number': card['collector_number'],
                                    'image_uris': card['image_uris'],
                                    'layout': card['layout'],
                                    'two_sided': False,
                                    'border_color': card['border_color']}

                    elif not card['layout'] == 'art_series': print (f"Unknown layout {card['layout']} for card {card['name']}")


                # Save parsed data to a file for future use
                with open(f'{filepath.split('/')[0]}/parsed_{filepath.split('/')[-1]}', 'w', encoding="utf-8") as outfile:
                    outfile.write(orjson.dumps(card_dict).decode())
                print(f"Parsed {len(card_dict)} cards from {filepath}")
                # collect garbage to free up memory
                # gc.collect()

        # crash the program if the file is not loaded correctly
        except orjson.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in {filepath}")
            raise e
        except MemoryError as e:
            print(f"Out of memory while reading {filepath}. {len(card_dict)} cards into the file. Error: {e}")
            raise e
        except FileNotFoundError as e:
            print(f"Error: File not found at {filepath}")
            raise e

    logging.info(f"Loaded {len(card_dict)} cards from {filepath}")
    return card_dict

def add_card_data_to_decklist(card_data: dict) -> None:
    """
    Add card data to the decklist dictionary.
    :param card_data: Dictionary containing card data
    :return: None
    """
    i = 0
    copies = card_data['copies']
    card_data.pop('copies', None)  # Remove copies from card_data
    while i < copies:
        if 'sides' in card_data and card_data['sides'] is not None and not conf['two_sided'] and not card_data['custom']:
            for side in card_data['sides']:
                decklist.append(side)
        else:
            decklist.append(card_data)
        i += 1

def read_decklist(filepath):
    line_count = 0
    try:
        with open(filepath, 'r', encoding='utf-8') as decklist_file:
            for decklist_line in decklist_file:
                line_count += 1
                decklist_line = decklist_line.strip()
                if decklist_line.startswith("#") or decklist_line == "":
                    continue
                copies = int(decklist_line[:decklist_line.index(" ")])
                decklist_line = decklist_line[decklist_line.index(" ")+1:].strip()
                if "|" in decklist_line:
                    cardfaces = []
                    cardfaces = decklist_line.split("||")
                    cards = []
                    for card in cardfaces:
                        card = card.strip()
                        if card.strip().startswith("*"):
                            # Custom card, skip card_data lookup
                            name = card[+1:]
                            card = {'name': name, 'key': name, 'black_border': False, 'custom': True}
                            cards.append(card)
                        else:
                            # Normal card, lookup in card_data
                            cards.append(card_data_lookup(card))
                    add_card_data_to_decklist({'copies': copies, 'sides': cards, 'two_sided': True, 'custom': True})
                    continue
                if decklist_line.strip().startswith("*"):
                    # Custom card, skip card_data lookup
                    name = decklist_line[decklist_line.index("*")+1:].strip()
                    entry = {'name': name, 'key' : name, 'two_sided': False, 'black_border': False, 'custom': True, 'copies': copies}
                    add_card_data_to_decklist(entry)
                    continue
                # Normal card, lookup in card_data
                entry = card_data_lookup(decklist_line)
                entry.update({'copies': copies})
                add_card_data_to_decklist(entry)
        return
    except FileNotFoundError:
        logging.error(f"Decklist file {filepath} not found.")
        raise FileNotFoundError(f"Decklist file {filepath} not found.")
    except Exception as e:
        logging.error(f"Error reading decklist file {filepath} on line {line_count}: {e}")
        raise e

def card_data_lookup(decklist_line:str) -> dict:
    data = {}
    set_symbol = decklist_line[decklist_line.index("(") + 1:decklist_line.index(")")].lower()
    set_number = decklist_line[len(decklist_line) - decklist_line[::-1].index(" "):].strip()
    key = f"{set_symbol}-{set_number}"
    force_side = 0
    if decklist_line.startswith("!!"):
        force_side = 2
        decklist_line = decklist_line[2:].strip()
        key = f"{key}_B"
    elif decklist_line.startswith("!"):
        force_side = 1
        decklist_line = decklist_line[1:].strip()
        key = f"{key}_A"
    try:

        data = card_data[key]
    except KeyError as e:
        raise KeyError(f"Card {decklist_line} not found in card data. Please check the decklist format or the card data.") from e

    return {
        'name': decklist_line[:decklist_line.index("(") - 1],
        'key': key,
        'set_symbol': decklist_line[decklist_line.index("(") + 1:decklist_line.index(")")].lower(),
        'set_number': decklist_line[len(decklist_line) - decklist_line[::-1].index(" "):].strip(),
        'black_border': True if data['border_color'] == "black" else False,
        'two_sided': data['two_sided'] if not force_side>0 else False,
        'force_side': force_side,
        'sides': data['faces'] if data['two_sided'] and force_side==0 else None,
        'layout': data['layout'],
        'custom': False,
        'image_uris': data['image_uris'] if 'image_uris' in data else {
            'small': 'custom_cards/{key}.jpg',
            'normal': 'custom_cards/{key}.jpg',
            'large': f'custom_cards/{key}.jpg',
            'png': f'custom_cards/{key}.png',
            'art_crop': None,
            'border_crop': None
        }
    }

def fetch_bulk_json():
    headers = {'User-Agent': conf['user_agent'],
               'Accept': conf['accept']}
    response = requests.get('https://api.scryfall.com/bulk-data/default-cards', headers=headers)
    response.raise_for_status()
    json_response = response.json()
    bulk_json_uri = json_response['download_uri']
    local_filename = f"scryfall_bulk_json/{bulk_json_uri.split('/')[-1]}"

    request = Request(bulk_json_uri, headers=headers)
    if not os.path.exists(local_filename):
        logging.info('Downloading new scryfall ')
        with urllib.request.urlopen(request) as response, open(local_filename, 'wb') as out_file:
            out_file.write(response.read())
    return local_filename

def resize_image_to_card_size(image: Image.Image, dpi: int) -> Image.Image:
    """
    Resize an image to the target card size in pixels at the specified DPI.
    :param image: PIL Image object
    :param dpi: dots per inch for the image
    :return: resized PIL Image object converted to "RGB"
    """
    # Card size in mm
    # Convert mm to pixels
    return image.resize((const['card_width_px'], const['card_height_px']), Image.Resampling.LANCZOS).convert("RGB")

def correct_gamma(img:Image.Image) -> Image.Image:

    img_width, img_height = img.size
    # Ensure image is not empty before getting pixel
    if img_width == 0 or img_height == 0:
        logging.error('Gamma correction imput 0 size') 
        raise Exception 
    
    border_color = img.getpixel((int(img_width/2), int(img_height - img_height/50)))
    if border_color is None:
        logging.error('Gamma correction cant get border color') 
        raise Exception 
    # Handle grayscale and color images
    if isinstance(border_color, (tuple, list)):
            border_gamma = sum(border_color[:3]) / 3
    elif isinstance(border_color, (int, float)):
        border_gamma = border_color
    else:
        logging.error('Gamma correction: Unknown format') 
        raise Exception 

    # Avoid infinite loops with extreme gamma values
    if border_gamma > 100:
        logging.error('Gamma correction: border color too bright')
        raise Exception
    
    while border_gamma > 3:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1 + border_gamma * 1 / 256)
        try:
            border_color = img.getpixel((int(img_width/2), int(img_height - img_height/50)))
        except IndexError:
            break # Exit if image becomes too small

        if isinstance(border_color, (tuple, list)):
             if len(border_color) >= 3:
                border_gamma = sum(border_color[:3]) / 3
             else:
                border_gamma = border_color[0] if border_color else 0
        elif isinstance(border_color, (int, float)):
            border_gamma = border_color
        else:
            break
        if border_gamma < 3:
            break
    return img

def fetch_image(image_url:str, destination:str, headers, key:str, custom:bool) -> None:
    img = None
    if not custom:
        parts = destination.split('/')
        dpi_destination = f"{parts[0]}/{conf['dpi']}/{parts[1]}/{parts[2]}"
        gc_path = dpi_destination[:-4] + f"_gc{os.path.splitext(dpi_destination)[1]}"
    else:
        parts = destination.split('/')
        dpi_destination = f"{parts[0]}/{conf['dpi']}/{parts[1]}"
        gc_path = dpi_destination[:-4] + f"_gc{os.path.splitext(dpi_destination)[1]}"

    if image_url is None:
        logging.error(f"Image URL for {key} is None. Skipping download.")
        return
    if custom:
        if not os.path.exists(dpi_destination):
            try:
                img = Image.open(destination)
                img.load()
            except Exception as e:
                logging.error(f"Error opening cached image {gc_path}: {e}")
                raise e # Do not proceed with missing images!
            img = resize_image_to_card_size(img, conf['dpi'])
            img.save(dpi_destination, const['image_format'])
            img.load()
        else: 
            try:
                img = Image.open(dpi_destination)
                img.load()
            except Exception as e:
                logging.error(f"Error opening cached image {dpi_destination}: {e}")
                raise e # Do not proceed with missing images!
        image_cashe.update({key:img})
        return
    
    if not os.path.exists(gc_path):
        if not os.path.exists(dpi_destination):
            if not os.path.exists(destination):
                logging.info(f"Downloading image {destination}")
                try:
                    img_bytes = requests.get(image_url, headers=headers).content
                    img = Image.open(io.BytesIO(img_bytes))
                    img.save(destination, const['image_format'])
                    img.load()
                except Exception as e:
                    logging.error(f"Error downloading or processing image {image_url}: {e}")
                    raise e # Do not proceed with missing images! 
            
            else:
                try:
                    img = Image.open(destination)
                    img.load()
                except Exception as e:
                    logging.error(f"Error opening cached image {destination}: {e}")
                    raise e # Do not proceed with missing images! 
                        
            img = resize_image_to_card_size(img, conf['dpi']) # Resize to card size in pixels at 600 DPI
            img.save(dpi_destination, const['image_format'])
            img.load()
        else: 
            try:
                img = Image.open(dpi_destination)
                img.load()
            except Exception as e:
                logging.error(f"Error opening cached image {dpi_destination}: {e}")
                raise e # Do not proceed with missing images!
            try:
                img = correct_gamma(img)
                img.save(gc_path)
                img.load()
                logging.info(f"Gamma correction applied to {dpi_destination}")
            except Exception as e:
                logging.error(f"Error applying gamma correction to {dpi_destination}: {e}")
                raise e # Do not proceed with missing images!     
    else:
        if conf['gamma_correction'] and not custom:
            try:
                img = Image.open(gc_path)
                img.load()
            except Exception as e:
                logging.error(f"Error opening cached image {gc_path}: {e}")
                raise e # Do not proceed with missing images!
        else:
            try:
                img = Image.open(dpi_destination)
                img.load()
            except Exception as e:
                logging.error(f"Error opening cached image {gc_path}: {e}")
                raise e # Do not proceed with missing images!

    
    # Add image data to cache
    image_cashe.update({key:img})
    return

def create_image_cache()    -> None:
    image_type = conf['image_type']
    image_format = const['image_format']
    dpi = conf['dpi']

    os.makedirs("image_cache/" + image_type, exist_ok=True)
    os.makedirs("image_cache/" + str(dpi) + "/" + image_type, exist_ok=True)
    os.makedirs("custom_cards/" + str(dpi), exist_ok=True)
    os.makedirs("cardbacks/" + str(dpi), exist_ok=True)
    counter = 0
    headers = {'User-Agent': conf['user_agent'],
            'Accept': conf['accept']}
    image_cashe_timer_start = time.perf_counter()
    with ThreadPoolExecutor(conf['worker_threads']) as executor:

        for decklist_line in decklist:
            image_uri = ""
            if 'sides' in decklist_line and decklist_line['sides'] is not None:
                if decklist_line['sides'][0]['force_side'] == 2:
                    a =2
                    # Force side B, skip side A

            if decklist_line['sides'] is not None:
                for side in decklist_line['sides']:
                    if side['custom']:
                        executor.submit(fetch_image, f"custom_cards/{side['name']}.png", f"custom_cards/{side['name']}.{image_format}", headers,side['key'],True)
                        continue
                    layout = side['layout']
                    # Check if the image already exists in the cache as a one-sided or two-sided card and if the name starts with the marker "*" denoting a custom card
                    # sleep after every downloading thread is started to avid losing api
                    if not decklist_line['two_sided'] :
                        image_uri = card_data[f"{side['key']}"]['image_uris'][image_type]
                        destination = f"image_cache/{image_type}/{side['key']}.{image_format}"
                        key = side['key']
                        executor.submit(fetch_image, image_uri, destination, headers ,key,side['custom'])
                        if not os.path.exists(destination):
                            counter += 1
                            sleep(0.1)
                        continue

                    if decklist_line['two_sided']:
                        for side in decklist_line['sides']:
                            image_uri = side['image_uris'][image_type]
                            destination = f"image_cache/{image_type}/{side['key']}.{image_format}"
                            executor.submit(fetch_image, image_uri, destination, headers ,side['key'],side['custom'])
                            if not os.path.exists(destination):
                                counter += 1
                                sleep(0.1)
                        
                        continue
                    raise Exception(f"Unknown card layout {layout}")
                continue
            key = decklist_line['key']
            name = decklist_line['name']
            if decklist_line['custom']:
                executor.submit(fetch_image, f"custom_cards/{name}.png", f"custom_cards/{name}.{image_format}", headers ,name,True)
                counter += 1
                continue

                # Check if the image already exists in the cache as a one-sided or two-sided card and if the name starts with the marker "*" denoting a custom card
            
            

            if not decklist_line['two_sided']:
                
                image_uri = card_data[f"{key}"]['image_uris'][image_type]
            destination = f"image_cache/{image_type}/{key}.{image_format}"
            executor.submit(fetch_image, image_uri, destination, headers ,key,decklist_line['custom'])
            if not os.path.exists(destination):
                counter += 1
                sleep(0.1)
            continue

            
        # Fech backside if needed
        if conf['custom_backside'] and conf['two_sided']:
            if os.path.exists(f"cardbacks/{conf['backside']}"):
                #logging.info(f"Loading backside {conf['backside']}")
                executor.submit(fetch_image, f"cardbacks/{conf['backside']}", f"cardbacks/{conf['backside']}", headers, "back", True)
        
        # --- Wait for all threads to finish ---
        executor.shutdown(wait=True)
    ImageCacheTimerEnd = time.perf_counter()
    logging.info(f"Downloaded {counter} new images")

    logging.info(f"Image cache created in {ImageCacheTimerEnd - image_cashe_timer_start:.2f} seconds.")

def render_page(page_index:int, side:int) -> None:
    """
    Render a page with 9 cards using PIL and save as a temporary image file.
    :param page_index: Index of the page to render
    :param side: Side of the cards to render (0 for front, 1 for back)
    :return: None
    """
    card_index_start = page_index * 9
    deck_size = const['deck_size']
    if card_index_start >= deck_size: return

    # Create a blank A4 image in pixels at 600 DPI
    page_image = Image.new('RGB', (const['page_width_px'], const['page_height_px']), color = (255, 255, 255)) # White background
    draw = ImageDraw.Draw(page_image)
    # draw background rectangle
    draw.rectangle(const['bg_box'], fill=(0, 0, 0),width=0)
    

    do_B_side_next = False

    card_index = card_index_start
    for row_index in range(3):
        for col_index in range(3):
            if card_index < deck_size:
                image_placement_time_start = time.perf_counter()
                card = decklist[card_index]

                # --- Determine the key for the image ---
                key = None
                if 'sides' in card and card['sides'] is not None:
                    key = f"{card['sides'][side]['key']}"
                else:
                    key = card['key']

                if side == 1:
                    if conf['custom_backside'] and (not conf['two_sided'] or not card['two_sided']):
                        if card['two_sided'] and not do_B_side_next: do_B_side_next = True
                        else: do_B_side_next = False
                        key = 'back'
                    elif card['two_sided'] and conf['two_sided']:
                        if card['custom']:
                            key = card['sides'][1]['key']
                        # If not custom, key is already set correctly above

                # --- Get image from cache ---
                img = image_cashe[key]

                if img is not None:
                    # --- Calculate image position in pixels ---
                    # Card positions are already calculated in pixels in generate_constants
                    # --- to aligne backside with the front draw_x needs to be fliped for the other side
                    x_index = col_index
                    if side == 1: x_index = 2 - col_index
                    draw_x = const['card_positions_px'][row_index][x_index][0]
                    draw_y = const['card_positions_px'][row_index][x_index][1]

                    # --- Paste Image onto the page ---
                    page_image.paste(img, (draw_x, draw_y))

                    #print(f"Placed {deck[card_index]['name']},{image_name}")
                else:
                    logging.error(f"Image not found in cache for key: {key}.")
                    raise Exception


                card_index += 1
                # --- Perfornance logging ---
                image_placement_time_end = time.perf_counter()
                image_placement_time = image_placement_time_end - image_placement_time_start
                #logging.info(f"Placed {key} in {(image_placement_time*100):0f} milliseconds")
                image_placement_times.append(image_placement_time)

    # Draw_reference_points (in pixels)
    if conf['reference_points']:
        for rect in const['marker_rects']:
                draw.rectangle(rect, fill=(0, 0, 0),width=0)

    # store results in pages dict
    buffer_time_start = time.perf_counter()
    buffer = io.BytesIO()
    page_image.save(buffer, format='PNG')
    buffer.seek(0)
    buffer_time_end = time.perf_counter()
    page_buffer_time = buffer_time_end - buffer_time_start 
    logging.info(f"Buffered page {page_index} {'front' if side == 0 else 'back'} in {(page_buffer_time*100):0f} milliseconds")
    
    buffer_time_start = time.perf_counter()
    pages[f"{page_index},{side}"] = io.BytesIO(img2pdf.convert(buffer,layout_fun=const['A4']))
    buffer_time_end = time.perf_counter()
    page_buffer_time = buffer_time_end - buffer_time_start 
    logging.info(f"Img2pdf for page {page_index} {'front' if side == 0 else 'back'} in {(page_buffer_time*100):0f} milliseconds")
    #pages[f"{page_index},{side}"] = page_image

def render_pages():
    # --- Fill image cache with images ---
    logging.info("Loading Images into cache...")
    create_image_cache()

    # --- Render pages as images ---
    logging.info("Rendering pages as images...")
    global pages
    with ThreadPoolExecutor(max_workers=conf['worker_threads']) as executor: # Use a config for render threads
        
        for i in range(const['total_pages']):
            logging.info(f'Submitting render page {i} front')
            executor.submit(render_page, i, 0)
        if conf['two_sided']:
            for i in range(const['total_pages']):
                logging.info(f'Submitting render page {i} back')
                executor.submit(render_page, i, 1)

        executor.shutdown(wait = True)

    logging.info("Finished rendering pages as images.")

def generate_constants() -> dict:
    # --- Constants (in mm) ---
    card_width_mm = 63
    card_height_mm = 88
    spacing_mm = conf['spacing']
    bg_box_margin_mm = 2 # This might not be needed anymore with PIL drawing
    dpi = conf['dpi'] # Fixed DPI for rendering

    # --- Convert mm to pixels ---
    mm_to_px = lambda val_mm: int(val_mm * dpi / 25.4)

    card_width_px = mm_to_px(card_width_mm)
    card_height_px = mm_to_px(card_height_mm)
    spacing_px = mm_to_px(spacing_mm)
    bg_box_margin_px = mm_to_px(bg_box_margin_mm)

    # --- A4 Page Dimensions (in pixels at 600 DPI) ---
    page_width_px = mm_to_px(210)
    page_height_px = mm_to_px(297)

    grid_width_px = 3 * card_width_px + 2 * spacing_px
    grid_height_px = 3 * card_height_px + 2 * spacing_px

    x_axis_offset_mm = float(conf["x_axis_offset"])
    x_axis_offset_px = mm_to_px(x_axis_offset_mm)


    # --- Calculate Grid Offsets (in pixels) ---
    grid_x_offset_px = ((page_width_px - grid_width_px) / 2 ) + x_axis_offset_px
    grid_y_offset_px = ((page_height_px - grid_height_px) / 2)

    # --- Calculate Grid Center (in pixels) ---
    grid_center_x_px = page_width_px / 2 + x_axis_offset_px
    grid_center_y_px = page_height_px / 2

    # --- calculate black backroud box size and position ---
    bg_box_width_px = card_width_px*3+bg_box_margin_px*2
    bg_box_height_px = card_height_px*3+bg_box_margin_px*2
    bg_box_position = [grid_x_offset_px - bg_box_margin_px,grid_y_offset_px - bg_box_margin_px]
    bg_box = [bg_box_position[0],bg_box_position[1],bg_box_position[0]+ bg_box_width_px,bg_box_position[1] + bg_box_height_px]

    
    # --- Location marker sets (converted to pixels if needed in render_page) ---
    marker_vectors = [[mm_to_px(2),mm_to_px(2)],[-mm_to_px(2),-mm_to_px(2)]] # Keep original for reference if needed
    marker_iteration = [[1,1],[1,-1],[-1,-1],[-1,1]] # Keep original for reference if needed
    marker_rects = []
    for iterator_vectors in marker_iteration:
                for vector in marker_vectors:
                    pos = [grid_center_x_px + mm_to_px(iterator_vectors[0] * 193/2), grid_center_y_px + mm_to_px(iterator_vectors[1] * 278/2)]
                    sorted_x = [pos[0],pos[0]+vector[0]]
                    sorted_y = [pos[1],pos[1]+vector[1]]
                    sorted_x.sort()
                    sorted_y.sort()
                    marker_rects.append([sorted_x[0], sorted_y[0], sorted_x[1], sorted_y[1]])
    # --- Calculate Card Positions (in pixels) ---
    card_positions_px = []

    for row in range(3):
        card_positions_px.append([])
        for pos in range(3):
            x = grid_x_offset_px +  pos * (card_width_px + spacing_px)
            # Y calculation needs adjustment for pixel coordinates (0,0 is top-left in PIL)
            # We want the bottom-left corner of the card to be at the calculated position
            # The grid_y_offset_px is the distance from the bottom of the page to the bottom of the grid
            # So, the y position for a card is page_height_px - (grid_y_offset_px + (row + 1) * card_height_px + row * spacing_px)
            y = page_height_px - (grid_y_offset_px + (3 - row) * card_height_px + row * spacing_px)
            card_positions_px[row].append([int(x), int(y)]) # Ensure pixel coordinates are integers
    a4inpt = (img2pdf.mm_to_pt(210),img2pdf.mm_to_pt(297))
    A4 = img2pdf.get_layout_fun(a4inpt)
    """bg_box_per_card = []
    for row in range(3):
        bg_box_per_card.append([])
        for pos in range(3):
            x1 = card_positions_px[row][pos][0] - bg_box_margin_px
            y1 = card_positions_px[row][pos][1] 
            bg_box_per_card[row].append([int(x1), int(y1),int(x2),int(y2)],) # Ensure pixel coordinates are integers"""

    # --- Determine image file extension ---
    image_type = conf['image_type']
    match image_type:
        case 'small'|'normal'|'large'|'art_crop'|'border_crop':
            image_format = 'jpg'
        case 'png':
            image_format = 'png'
        case _:
            logging.error(f"Unknown image type {image_type}")
            raise Exception(f"Unknown image type {image_type}")

    return {
        'deck_size': len(decklist),
        'total_pages': (len(decklist) + 8) // 9,  # 9 cards per page
        'card_width_px': card_width_px, # Keep mm values for reference
        'card_height_px': card_height_px,
        'spacing_mm': spacing_mm,
        'bg_box': bg_box,
        'page_width_px': page_width_px,
        'page_height_px': page_height_px,
        'marker_rects': marker_rects,
        'card_positions_px': card_positions_px, # Store positions in pixels
        'image_format': image_format,
        'dpi': dpi, # Store DPI
        'A4': A4,
        'commander': decklist[0]['name']
    }

def merge_pages() -> None:
    """
    Merge all temporary page image files into a single PDF file using img2pdf.
    :return: None
    """
    global pages, conf, const
    
    output_filename = const['decklist']
    if const['decklist'] != "decklist.txt":
        output_filename = const['commander']
    if not output_filename.endswith('.pdf'):
        output_filename += '.pdf'
    #output = bytes()
    merger = PdfMerger()
    pattern = []
    logging.info(f"Merging {len(pages)} page images into {output_filename}")
    #def merge(key1,key2): return pages[key1].join(pages[key2])
    pages_imput_array = []
    #with ThreadPoolExecutor(conf['worker_threads']) as executor:
    # Set the order in wich the pages are to be printed
    if conf['two_sided'] and conf['stagger']:
        pattern = [[0,0],[1,0],[0,1],[1,1]]
    elif conf['two_sided'] and not conf['stagger']:
        pattern = [[0,0],[0,1],[1,0],[1,1]]
    elif not conf['two_sided']:
        pattern = [[0,0],[1,0]]
    i = 0
    
    while i < const['total_pages']:

        for set in pattern:
            key = f"{i+set[0]},{set[1]}"
            if i+set[0] == const['total_pages']: continue
            merger.append(pages[key])
            pages_imput_array.append(pages[key])
        i+=2
    try:
        # write output.pdf
        with open("output/"+output_filename, "wb") as f:
            merger.write(f)
        logging.info(f"PDF created successfully at {output_filename}")

    except Exception as e:
        logging.error(f"Error merging pages with img2pdf: {e}")
        raise e

def write_config(conf_list:list):
    with open('decklist_to_pdf.ini', 'a') as config_file:
        for config in conf_list:
            match config:
                case 'decklist_path':
                    config_file.write(f"""
# relative path to decklist listing unique cards one per line in of the formats:
# copies name (SET) collector_number
# copies name (SET) collector_number | backside.jpg/*.png
# copies name (SET) collector_number | (SET) collector_number
decklist_path:{conf['decklist_path']}
""")
                case 'two_sided':
                    config_file.write(f"""
# two sided printing
two_sided:{conf['two_sided']}
""")
                case 'custom_backside':
                    config_file.write(f"""
# has custom backside
custom_backside:{conf['custom_backside']}
""")
                case 'backside':
                    config_file.write(f"""
# default backside image
backside:{conf['backside']}
""")
                case 'pdf_path':
                    config_file.write(f"""
# relative export path for pdf
pdf_path:{conf['pdf_path']}
""")
                case 'image_type':
                    config_file.write(f"""
# possible image types are small / normal / large / png / art_crop / border_crop
image_type:{conf['image_type']}
""")
                case 'spacing':
                    config_file.write(f"""
# spacing between cards in mm
spacing:{conf['spacing']}
""")
                case 'mode':
                    config_file.write(f"""
# default - for regular black border cards. Image size is 63x88 mm with 2 mm black spacing between cards
# bleed edge - for full art cards. Image size is 65x90.79 mm with no spacing between cards
mode:{conf['mode']}
""")
                case 'gamma_correction':
                    config_file.write(f"""
# gamma correction for images
gamma_correction:{conf['gamma_correction']}
""")
                case 'reference_points':
                    config_file.write(f"""
# toggle reference point True/False
reference_points:{conf['reference_points']}
""")
                case 'stagger':
                    config_file.write(f"""
# stagger pages for faster 2 sided printing with slow printers (Front,Front,Back,Back)
stagger: {conf['stagger']}
""")
                case 'x_axis_offset':
                    config_file.write(f"""
# move everything on the x_axis
x_axis_offset:{conf['x_axis_offset']}
""")
                case 'user_agent':
                    config_file.write(f"""
# user agent for scryfall bulk json download
user_agent:{conf['user_agent']}
""")
                case 'accept':
                    config_file.write(f"""
# accept header for scryfall bulk json download
accept:{conf['accept']}
""")
                case 'worker_threads':
                     config_file.write(f"""
# number of threads to use for rendering pages and image proccessing
worker_threads:{conf['worker_threads']}
""")
                case 'dpi':
                    config_file.write(f"""
# pixel density for printing
dpi:{conf['dpi']}
""")
    config_file.close()

def read_config():
    keys = list(conf.keys())
    conf_count = 0
    conf_update_check = conf.copy()
    conf_update_check.pop('bulk_json_path', None) # Use .pop with default to avoid KeyError
    for a in conf_update_check.keys():
        conf_update_check[a] = False
    try:
        with open("decklist_to_pdf.ini", "r") as file:
            conf_count = 0
            for line in file:
                if not line.strip() or line.lstrip().startswith('#'):
                    continue
                parts = line.strip().split(':')
                if len(parts) < 2: # Skip lines that don't have a key:value structure
                    continue
                key = parts[0].strip()
                value = ':'.join(parts[1:]).strip() # Handle cases where value contains ':'

                if key in keys:
                    conf_count += 1
                    if value == 'True':
                        conf[key] = True
                    elif value == 'False':
                        conf[key] = False
                    else:
                        # --- check if the value is a number and convert it if true ---
                        try:
                            conf[key] = int(value)
                        except ValueError:
                            try:
                                conf[key] = float(value)
                            except ValueError:
                                conf[key] = value # Keep as string if not int or float
                    if key in conf_update_check: # Check if key exists before setting to True
                        conf_update_check[key] = True

    except FileNotFoundError:
        logging.error("decklist_to_pdf.ini inaccessable.")
        # The function is only called if the file is detected something must be wrongw with premissions if you cant readit. 
        raise Exception

    # Write missing config entries
    missing_configs = [config for config, found in conf_update_check.items() if not found]
    if missing_configs:
        logging.info(f"Writing missing configuration entries: {', '.join(missing_configs)}")
        write_config(missing_configs)


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    # Time runtime
    full_start_time = time.perf_counter()
    logging.info("Starting decklist_to_pdf script")
    # Default configuration values
    conf = {
        'decklist_path' : 'decklist.txt',
        'two_sided': False,
        'custom_backside': False,
        'backside': 'back.png',
        'pdf_path' : 'output.pdf',
        'image_type' : 'png',
        'spacing' : 0,
        'mode' : 'default',
        'gamma_correction' : True,
        'reference_points' : True,
        'stagger': True,
        'x_axis_offset' : 0.75,
        'user_agent': 'decklist_to_pdf/0.1',
        'accept': 'application/json;q=0.9,*/*;q=0.8',
        'worker_threads': 4,
        'dpi': 600
    }
    conf.update({'bulk_json_path':fetch_bulk_json()})


    if not os.path.exists('decklist_to_pdf.ini'):
        write_config(list(conf.keys()))
    else:
        logging.info("Loading configuration from decklist_to_pdf.ini")
        read_config()


    load_scryfall_data_start = time.perf_counter()
    logging.info(f"Loading Scryfall bulk json to dictionary from {conf['bulk_json_path']}")
    card_data = load_card_dictionary(conf['bulk_json_path'])
    load_scryfall_data_end = time.perf_counter()
    logging.info(f"Finished in {load_scryfall_data_end - load_scryfall_data_start:.2f} seconds")

    logging.info(f"Reading decklist from input/""input"".text")
    decklist = []
    decklist_name = input("Enter decklist name (default: decklist.txt): ").strip()
    conf['decklist_path'] = f"input/{decklist_name}.txt"
    read_decklist(conf['decklist_path'])
    logging.info(f"Found {len(decklist)} cards to print in decklist")
    
    # Set up constants
    const = generate_constants()
    const.update({'decklist': decklist_name})

    logging.info("Creating PDF")
    image_cashe = {} # Initialize image_cashe here
    image_placement_times = []
    make_pdf_start_time = time.perf_counter()
    pages = {} # Initialize pages here

    render_pages()
    # --- Merge pages into a single PDF ---
    merge_time_start = time.perf_counter()
    logging.info(f"Merging pages into PDF")
    merge_pages()
    merge_time_end = time.perf_counter()
    logging.info(f"PDF merged in {(merge_time_end - merge_time_start)*1000:.0f} milliseconds")

    make_pdf_end = time.perf_counter()
    logging.info(f"PDF made in {make_pdf_end - make_pdf_start_time:.2f} seconds")
    full_end = time.perf_counter()
    avaarage_image_placement_time = sum(image_placement_times) / len(image_placement_times) if image_placement_times else 0
    logging.info(f"Finished in {full_end - full_start_time:.2f} seconds, average image placement time: {(avaarage_image_placement_time)*1000:.0f} milliseconds")
