import urllib.request
from concurrent.futures import ThreadPoolExecutor
from time import sleep, time
from urllib.request import urlretrieve, Request
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm,inch
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfWriter, PdfReader
from PIL import Image, ImageEnhance
import time
import requests
import logging
import orjson
import os
import io
import re
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
    global decklist
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

def rezise_image(image, target_size=[63, 88], dpi=600) -> Image.Image:
    """
    Resize an image to the target size in mm at the specified DPI.
    :param image: PIL Image object
    :param target_size: tuple of (width, height) in mm
    :param dpi: dots per inch for the image
    :return: resized PIL Image object converted to "RGB"
    """
    target_width_px = int(target_size[0] * dpi / inch)  # Convert mm to pixels
    target_height_px = int(target_size[1] * dpi / inch)
    return image.resize((target_width_px, target_height_px), Image.Resampling.LANCZOS)

def fetch_image(image_url:str, destination:str, headers, key:str, custom:bool) -> None:
    img = None

    if image_url is None:
        logging.error(f"Image URL for {key} is None. Skipping download.")
        return
    if not os.path.exists(destination):
        logging.info(f"Downloading image {destination}")
        img_bytes = requests.get(image_url, headers=headers).content
        img = Image.open(io.BytesIO(img_bytes))
        img.load()
        img = rezise_image(img, target_size=[63, 88], dpi=600)
        img.save(destination,const['image_format'])

    else:
        img = Image.open(destination)
        img.load()


    if conf['gamma_correction']:
        gc_path = destination[:-4] + f"_gc{os.path.splitext(destination)[1]}"
        if not os.path.exists(gc_path):
            img = correct_gamma(img)
            img.save(gc_path)
            logging.info(f"Gamma correction applied to {destination}")
        else:
            img = Image.open(gc_path)
            img.load()

    
    # Calculate scaling factor (fit image within rectangle)
    scale_x = (const['card_width'] * mm) / img.width
    scale_y = (const['card_height'] * mm) / img.height
    #scale = min(scale_x, scale_y)

    # Calculate centered image position
    draw_width = img.width * scale_x
    draw_height = img.height * scale_y
    data = ImageReader(img)
    #pages.drawImage(data, -10000, -10000, img.width, img.height)
    #dummy_canvas = canvas.Canvas(io.BytesIO(), pagesize=A4)
    #dummy_canvas.drawImage(data, -10000, -10000, img.width, img.height)
    #dummy_canvas.saveState()


    # Create image data dictionary
    img_data:dict = {
        'data': data,
        'width': draw_width,
        'height': draw_height,
    }
    # Add image data to cache
    image_cashe[key] = img_data
   
    return

def correct_gamma(img_in) -> Image.Image:
    #convert bytestream to image
    img = Image.Image()
    if isinstance(img_in, Image.Image):
        img = img_in
    else :img = Image.open(io.BytesIO(img_in))
        
    
    img_width, img_height = img.size
    border_color = img.getpixel((int(img_width/2), int(img_height - img_height/50)))
    if border_color is None:
        return img
    # Handle grayscale and color images
    if isinstance(border_color, (tuple, list)):
        border_gamma = sum(border_color[:3]) / 3
    elif isinstance(border_color, (int, float)):
        border_gamma = border_color
    else:
        
        return img
    
    while border_gamma > 3:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1 + border_gamma * 1 / 256)
        border_color = img.getpixel((int(img_width/2), int(img_height - img_height/50)))
        if isinstance(border_color, (tuple, list)):
            border_gamma = sum(border_color[:3]) / 3
        elif isinstance(border_color, (int, float)):
            border_gamma = border_color
        else:
            break
        if border_gamma < 3:
            break
    return img

def create_image_cache()    -> None:
    image_type = conf['image_type']
    image_format = const['image_format']

    os.makedirs("image_cache/" + image_type, exist_ok=True)
    counter = 0
    headers = {'User-Agent': conf['user_agent'], 
            'Accept': conf['accept']}
    image_cashe_timer_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=12) as executor:
        
        for decklist_line in decklist:
            
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
                logging.info(f"Loading backside {conf['backside']}")
                executor.submit(fetch_image, f"cardbacks/{conf['backside']}", f"cardbacks/{conf['backside']}", headers, conf['backside'],True)
        
        # --- Wait for all threads to finish ---
        executor.shutdown(wait=True)
    ImageCacheTimerEnd = time.perf_counter()
    logging.info(f"Downloaded {counter} new images")

    # Warm up the image cashe reader to avoid issues with ReportLa
    """warmup_timer_start = time.perf_counter()
    logging.info("Warming up image cache...")
    with ThreadPoolExecutor(max_workers=16) as executor:
        for key in image_cashe.keys():
            executor.submit(warm_up_image, key)
        executor.shutdown(wait=True)
    warmup_timer_end = time.perf_counter()"""
    logging.info(f"Image cache created in {ImageCacheTimerEnd - image_cashe_timer_start:.2f} seconds.")

def warm_up_image(key:str) -> None:
    """
    Warm up the image cache by drawing the image on a dummy canvas.
    This is needed to avoid issues with ReportLab when drawing images.
    """
    global image_cashe
    img = image_cashe[key]['data']
    dummy_canvas = canvas.Canvas(io.BytesIO(), pagesize=A4)
    dummy_canvas.drawImage(img, -10000, -10000, image_cashe[key]['width'], image_cashe[key]['height'])
    dummy_canvas.save()
    image_cashe[key]['data'] = img  # Update the image data to be a ImageReader object
    return
# TODO: Bleed edge mode
def render_page(page_index:int, side:int) -> None:
    """
    Render a page with 9 cards.
    :param page_index: Index of the page to render
    :param side: Side of the cards to render (0 for front, 1 for back)
    :return: None
    """
    global pages, deck_data, image_cashe, conf
    card_index = page_index * 9
    deck_size = const['deck_size']
    if card_index >= deck_size: return
    page = canvas.Canvas(io.BytesIO(), pagesize=A4)
    page.setFillColorRGB(0, 0, 0)  # Black
    page.setLineWidth(0)
    
    do_B_side_next = False
    
    #print(f"Two sided: {conf['two_sided']}, Custom Backside {conf['custom_backside']}")
    
    #print(f"Working on side {working_on+1} of {sides}")
    # --- Create pages ---
    #if conf['two_sided'] and working_on == 1: output_filename = output_filename[:-4] + "_back.pdf"
    
    
    #while card_index < stop_at and card_index < deck_size:
    # --- Black Background Rectangle ---
    #page.rect((const['grid_x_offset'] - conf['bg_box_margin']) * mm , (const['grid_y_offset'] - conf['bg_box_margin']) * mm , (const['grid_width'] + 2*conf['bg_box_margin']) * mm , (const['grid_height'] + 2*conf['bg_box_margin']) * mm , stroke=0 , fill=1)
    
    for row in const['card_positions']:
        for i  in range(3):

            if card_index < deck_size:
                image_placement_time_start = time.perf_counter()
                card = decklist[card_index]
                # --- Handle Custom cards ---
                if 'sides' in card and card['sides'] is not None:
                    key = f"{card['sides'][side]['key']}"
                else:
                    key = card['key']
                
                if side == 1:
                    if conf['custom_backside'] and (not conf['two_sided'] or not card['two_sided']):
                        if card['two_sided'] and not do_B_side_next: do_B_side_next = True
                        else: do_B_side_next = False
                        key = conf['backside']
                    elif card['two_sided'] and conf['two_sided']:
                        if card['custom']:
                            key = card['sides'][1]['key']
                # Draw Rectangle (optional, for debugging/border)
                #c.rect((grid_x_offset - spacing) * mm , (grid_y_offset - spacing) * mm , (grid_width + 2*spacing) * mm , (grid_height  + grid_x_offset + 2*spacing) * mm , stroke=0 ,  fill=1)

                #c.setFillColorRGB(1, 1, 1) # White
                #c.rect(x * mm, y * mm, rectangle_width * mm, rectangle_height * mm, stroke=1, fill=0)
                
                # --- Image Placement ---
                #if side == 0 or conf['custom_backside'] or decklist[card_index]['two_sided']:
                try:
                    
                    img = image_cashe[key]
                    
                    
                    
                    # --- Draw Grid of Images ---

                    
                    xindex = i
                    if conf['two_sided'] and side == 1: xindex = 2 - i
                    draw_x = row[xindex][0] * mm + (const['card_width'] * mm - img['width']) / 2
                    draw_y = row[i][1] * mm + (const['card_height'] * mm - img['height']) / 2
                    # --- Black Background Rectangle per card ---
                    page.rect(draw_x - const['spacing'] * mm , draw_y - const['spacing'] * mm , img['width'] + 2*const['spacing'] * mm , img['height'] + 2*const['spacing'] * mm , stroke=0 , fill=1)
                    page.drawImage(img['data'], draw_x, draw_y, img['width'], img['height'], mask='auto')
                    #print(f"Placed {deck[card_index]['name']},{image_name}")
                except Exception as e:

                    print(f"Error processing image {key}: {e}") # Handle image loading errors
                    raise e

                card_index += 1
                i += 1
                
                image_placement_time_end = time.perf_counter()
                image_placement_time = image_placement_time_end - image_placement_time_start
                #logging.info(f"Placed {key} in {(image_placement_time*100):0f} milliseconds")
                image_placement_times.append(image_placement_time)
        
        # Draw_reference_points
        if conf['reference_points']:
            for iterator_vectors in const['marker_iteration']:
                for vector in const['marker_vectors']:
                    page.rect(const['grid_center_x'] + iterator_vectors[0] * 193 * mm/2 , const['grid_center_y'] + iterator_vectors[1] * 278*mm/2 , vector[0] , vector[1] , stroke=0 , fill=1)
            
    
    #print(f"PDF created: {output_filename}")
    #if working_on == 1 or not conf['two_sided']: break
    #page.save()
    pages.update({f"{page_index},{side}":canvas_to_pdf_page(page)})

def render_pages():
    # --- Fill image cache with images ---
    logging.info("Loading Images into cache...")
    create_image_cache()
    with ThreadPoolExecutor(max_workers=32) as executor:
        i=0
        while  i < const['deck_size']//9+1:
            logging.info(f'rendering page {i} front')
            executor.submit(render_page,i, 0)
            i += 1
        if conf['two_sided']:
            i = 0
            logging.info(f'rendering page {i} back')
            while  i < const['deck_size']//9+1:
                executor.submit(render_page,i, 1)
                i += 1
        executor.shutdown(wait=True)

def generate_constants() -> dict:
    # --- Constants (in mm) ---
    card_width = 63
    card_height = 88
    spacing = conf['spacing']
    bg_box_margin = 2
    grid_width = 3 * card_width + 2 * spacing
    grid_height = 3 * card_height + 2 * spacing

    # --- A4 Page Dimensions (in mm) ---
    page_width, page_height = A4
    page_width_mm = page_width / mm
    page_height_mm = page_height / mm

    x_axis_offset = float(conf["x_axis_offset"])

    # --- Calculate Grid Offsets ---
    grid_x_offset = ((page_width_mm - grid_width) / 2 ) + x_axis_offset
    grid_y_offset = ((page_height_mm - grid_height) / 2) 
    
    
    # --- Location marker sets --- 
    marker_vectors = [[2*mm,2*mm],[-2*mm,-2*mm]]
    marker_iteration = [[1,1],[1,-1],[-1,-1],[-1,1]]

    # --- Calculate Grid Center ---
    grid_center_x = (page_width)/2 + x_axis_offset*mm
    grid_center_y = (page_height/2)

    # --- Calculate Card Positions ---
    card_positions = []

    
    for row in range(3):
        card_positions.append([])
        for pos in range(3):
            x = grid_x_offset + pos * (card_width + spacing*pos)
            y = page_height_mm - (grid_y_offset + (row + 1) * (card_height + spacing*row))
            card_positions[row].append([x, y])

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
        'card_width': card_width,
        'card_height': card_height,
        'spacing': spacing,
        'bg_box_margin': bg_box_margin,
        'grid_width': grid_width,
        'grid_height': grid_height,
        'page_width_mm': page_width_mm,
        'page_height_mm': page_height_mm,
        'grid_x_offset': grid_x_offset,
        'grid_y_offset': grid_y_offset,
        'grid_center_x': grid_center_x,
        'grid_center_y': grid_center_y,
        'marker_vectors': marker_vectors,
        'marker_iteration': marker_iteration,
        'card_positions': card_positions,
        'image_format': image_format
    }

def canvas_to_pdf_page(canvas_obj):
    """
    Convert a reportlab canvas to a PyPDF2 PageObject.
    """
    # Save the canvas to a BytesIO buffer
    buffer = canvas_obj.getpdfdata() if hasattr(canvas_obj, "getpdfdata") else None
    if buffer is None:
        # fallback for older reportlab: save to BytesIO
        pdf_buffer = io.BytesIO()
        canvas_obj.save()
        pdf_buffer.write(pdf_buffer.getvalue())
        pdf_buffer.seek(0)
    else:
        pdf_buffer = io.BytesIO(buffer)
    # Read the PDF page using PyPDF2
    pdf_reader = PdfReader(pdf_buffer)
    page = pdf_reader.pages[0]
    return page

def merge_pages() -> None:
    """
    Merge all pages into a single PDF file.
    :return: None
    """
    global pages, conf
    output_filename = conf['pdf_path']
    if not output_filename.endswith('.pdf'):
        output_filename += '.pdf'
    
    logging.info(f"Merging {len(pages)} pages into {output_filename}")
    
    pdf_writer = PdfWriter()
    side = ''
            
    if conf['stagger']:
        page_counter = 0
        stagger_pattern = [[0,0],[1,0],[0,1],[1,1]]
        while page_counter < const['total_pages']:
            for pattern in stagger_pattern:
                key = f"{page_counter + pattern[0]},{pattern[1]}"
                if key in pages:
                    
                    match pattern[1]:
                        case 0:
                            side = 'front'
                        case 1:
                            side = 'back'
                    logging.info(f"mergin page {page_counter + pattern[0]} {side}")
                    pdf_writer.add_page(pages[key])
            page_counter += 2
    else:
        for page in range(const['total_pages']):
            page = pages[f"{page},0"]
            pdf_writer.add_page(page)
    # Write the merged PDF to the output file
    with open(output_filename, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)

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
    config_file.close()

def read_config():
    keys = list(conf.keys())
    conf_count = 0
    conf_update_check = conf.copy()
    conf_update_check.pop('bulk_json_path')
    for a in conf_update_check.keys():
        conf_update_check[a] = False
    with open("decklist_to_pdf.ini", "r") as file:
        conf_count = 0
        for line in file:
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            parts = line.strip().split(':')
            for key in keys:
                match parts[0]:
                    case key:
                        conf_count += 1
                        conf[key] = parts[1]
                        if conf[key] == 'True':
                            conf[key] = True
                            break
                        if conf[key] == 'False':
                            conf[key] = False
                            break
                        # --- check if the value is a number and convert it if true ---
                        try:
                            conf[key] = int(conf[key])
                        except ValueError:
                            try:
                                conf[key] = float(conf[key])
                            except ValueError:
                                conf[key]
                        conf_update_check[key] = True
                        
                        break
    if conf_count < len(conf_update_check):
        for config in conf_update_check:
            if not conf_update_check[config]: write_config([config])
                
        
    

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
        'accept': 'application/json;q=0.9,*/*;q=0.8'
    }
    conf.update({'bulk_json_path':fetch_bulk_json()})

    
    

    if not os.path.exists('decklist_to_pdf.ini'):
        write_config(list(conf.keys()))
    else:
        logging.info("Loading configuration from decklist_to_pdf.ini")
        read_config()

    
    # Set up constants
    load_scryfall_data_start = time.perf_counter()

    logging.info(f"Loading Scryfall bulk json to dictionary from {conf['bulk_json_path']}")
    card_data = load_card_dictionary(conf['bulk_json_path'])
    
    load_scryfall_data_end = time.perf_counter()
    logging.info(f"Finished in {load_scryfall_data_end - load_scryfall_data_start:.2f} seconds")

    logging.info(f"Reading decklist from {conf['decklist_path']}")
    decklist = []
    read_decklist(conf['decklist_path'])
    logging.info(f"Found {len(decklist)} cards to print in decklist")

    

    logging.info("Creating PDF")
    # --- Generate constants ---
    const = generate_constants()
    image_cashe = {}
    image_placement_times = []
    make_pdf_start_time = time.perf_counter()
    pages = {}
    
    
    render_pages()
    # --- Merge pages into a single PDF ---
    output_filename = conf['pdf_path']
    logging.info(f"Merging pages into {output_filename}")
    merge_pages()
    
    make_pdf_end = time.perf_counter()
    logging.info(f"PDF made in {make_pdf_end - make_pdf_start_time:.2f} seconds")
    full_end = time.perf_counter()
    avaarage_image_placement_time = sum(image_placement_times) / len(image_placement_times) if image_placement_times else 0
    logging.info(f"Finished in {full_end - full_start_time:.2f} seconds, average image placement time: {avaarage_image_placement_time:.2f} seconds")

