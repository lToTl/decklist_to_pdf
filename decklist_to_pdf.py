import urllib
from concurrent.futures import ThreadPoolExecutor
from logging import Logger
from time import sleep
from urllib.request import urlretrieve, Request
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image, ImageEnhance
import requests
import logging
import orjson
import os
#import gc


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

                data = orjson.loads(bulk_json.read())
                # Read the next chunk of data
                for card in data:
                    #print(f"Processing card: {card['name']}")
                    # Create a key using set and collector_number
                    key = f"{card['set'].lower()}-{card['collector_number']}"
                    # Add needed card data to the dictionary
                    if card['layout'] in {'transform', 'modal_dfc', 'double_faced_token','reversible_card'}:
                            card_dict[key] = {'name': card['name'], 
                                            'set': card['set'],
                                            'collector_number': card['collector_number'],
                                            'image_uris': [card['card_faces'][0]['image_uris'],card['card_faces'][1]['image_uris']],
                                            'layout': card['layout'],
                                            'border_color': card['border_color']}
                    
                    else:
                        if card['layout'] in {
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
                                            'border_color': card['border_color']}
                        
                        else: 
                            if not card['layout'] == 'art_series': print (f"Unknown layout {card['layout']} for card {card['name']}")
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

# TODO: double sided format
def read_decklist(filepath, card_data):
    decklist = []
    with open(filepath, 'r', encoding='utf-8') as decklist_file:
        for decklist_line in decklist_file:
            copies = int(decklist_line[:decklist_line.index(" ")])
            name = decklist_line[decklist_line.index(" ") + 1:decklist_line.index("(") - 1]
            set_symbol = decklist_line[decklist_line.index("(") + 1:decklist_line.index(")")].lower()
            set_number = decklist_line[len(decklist_line) - decklist_line[::-1].index(" "):].strip()
            black_border = True
            if card_data[f"{set_symbol}-{set_number}"]['border_color'] != "black":
                black_border = False
            two_sided = False
            layout = card_data[f"{set_symbol}-{set_number}"]['layout']
            if layout == "transform" or layout == "modal_dfc" or layout == "double_faced_token":
                two_sided = True
            entry = {'copies': copies, 'name': name, 'set_symbol': set_symbol, 'set_number': set_number, 'two_sided': two_sided, 'black_border': black_border}
            decklist.append(entry)
    return decklist

def fetch_bulk_json(user_agent, accept):
    headers = {'User-Agent': user_agent,
               'Accept': accept}
    response = requests.get('https://api.scryfall.com/bulk-data/default-cards', headers=headers)
    response.raise_for_status()
    json_response = response.json()
    bulk_json_uri = json_response['download_uri']
    local_filename = f"scryfall_bulk_json/{bulk_json_uri.split('/')[-1]}"

    request = Request(bulk_json_uri, headers={'User-Agent': user_agent, 'Accept': accept})
    with urllib.request.urlopen(request) as response, open(local_filename, 'wb') as out_file:
        out_file.write(response.read())
    return local_filename


def fetch_image(image_url,  destination, user_agent, accept):
    headers = {'User-Agent': user_agent,
               'Accept': accept}
    img_data = requests.get(image_url, headers=headers).content
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
            name = decklist_line['name']
            set_symbol = decklist_line['set_symbol']
            set_number = decklist_line['set_number']
            layout = card_data[f"{set_symbol}-{set_number}"]['layout']
            
            if not (os.path.exists(f"image_cache/{image_type}/{set_symbol}-{set_number}.{image_format}") or
                (os.path.exists(f"image_cache/{image_type}/{set_symbol}-{set_number}_A.{image_format}"))):


                if layout == "normal" or layout == "token" or layout == "split" or layout == "flip":
                    logging.info(f"Downloading {name} -> {set_symbol}-{set_number}.{image_format}")
                    image_uri = card_data[f"{set_symbol}-{set_number}"]['image_uris'][image_type]
                    destination = f"image_cache/{image_type}/{set_symbol}-{set_number}.{image_format}"
                    executor.submit(fetch_image, image_uri, destination, config['user_agent'], config['accept'])
                    counter += 1
                    sleep(0.1)
                    continue

                if layout == "transform" or layout == "modal_dfc" or layout == "double_faced_token":
                    logging.info(logging.info(f"Downloading {name} -> {set_symbol}-{set_number}_A.{image_format}"))
                    
                    image_uri = card_data[f"{set_symbol}-{set_number}"]['image_uris'][0][image_type]
                    destination = f"image_cache/{image_type}/{set_symbol}-{set_number}_A.{image_format}"
                    executor.submit(fetch_image, image_uri, destination, config['user_agent'], config['accept'])
                    counter += 1
                    sleep(0.1)

                    logging.info(logging.info(f"Downloading {name} -> {set_symbol}-{set_number}_B.{image_format}"))
                    image_uri = card_data[f"{set_symbol}-{set_number}"]['image_uris'][1][image_type]
                    destination = f"image_cache/{image_type}/{set_symbol}-{set_number}_B.{image_format}"
                    executor.submit(fetch_image, image_uri, destination, config['user_agent'], config['accept'])
                    counter += 1
                    sleep(0.1)
                    continue
                raise Exception(f"Unknown card layout {layout}")
                
                
    logging.info(f"Downloaded {counter} new images")


def correct_gamma(image_path, image_format):
    img = Image.open(image_path)
    img_width, img_height = img.size
    border_color = img.getpixel((int(img_width/2), int(img_height - img_height/50)))
    border_gamma = (border_color[0] + border_color[1] + border_color[2])/3
    if border_gamma < 3:
        img.close()
        return False
    while border_gamma > 3:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1+border_gamma*1/256)
        border_color = img.getpixel((int(img_width/2), int(img_height - img_height/50)))
        border_gamma = (border_color[0] + border_color[1] + border_color[2])/3
    img.save(image_path[:-4] + f"_gc{image_format}")
    img.close()
    return True
        #print(f"Appling contrast of {1+border_gamma*3/256}")
# TODO: Bleed edge mode
def create_grid_pdf(image_folder, output_filename, deck, conf):
    """
    Generates a PDF with A4 pages, each containing a 3x3 grid of rectangles.
    Each rectangle displays an image from the specified folder.

    Args:
        :param image_folder: The path to the folder containing the images.
        :param output_filename: The name of the PDF file to be created.
        :param conf: configuration dictionary.
    """
    image_format = '.png'
    if conf['image_type'] != 'png':
        image_format = '.jpg'
    # --- Constants (in mm) ---
    card_width = 63
    card_height = 88
    spacing = 2
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

    # --- Get Image Files ---
    #image_files = sorted([f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))])  # Add more extensions if needed

    #if not image_files:
    #    print("No images found in the specified folder.")
    #    return
    

    # --- Calculate Grid Center ---
    grid_center_x = (page_width)/2 + x_axis_offset*mm
    grid_center_y = (page_height/2)

    # --- Calculate Card Positions ---
    card_positions = []
    for row in range(3):
        card_positions.append([])
        for pos in range(3):
            x = grid_x_offset + pos * (card_width + spacing)
            y = page_height_mm - (grid_y_offset + (row + 1) * (card_height + spacing) - spacing)
            card_positions[row].append([x, y])
    
    

    
    card_index = 0
    #deck_size = 0 
    #for card in deck: deck_size += card['copies']
    image_name = ""
    working_on = 0
    sides = 1
    do_B_side_next = False
    if conf['two_sided']: sides = 2
    print(f"Two sided: {conf['two_sided']}, Custom Backside {conf['custom_backside']}")
    while working_on < sides:
        print(f"Working on side {working_on+1} of {sides}")
        # --- Create PDF ---
        if conf['two_sided'] and working_on == 1: output_filename = output_filename[:-4] + "_back.pdf"
        c = canvas.Canvas(output_filename, pagesize=A4)
        card_index = 0
        copy_counter = 0
        while card_index < len(deck):
            # --- Black Background Rectangle ---
            c.setFillColorRGB(0, 0, 0)  # Black
            c.setLineWidth(0)
            #c.rect((grid_x_offset - spacing) * mm , (grid_y_offset - spacing) * mm , (grid_width + 2*spacing) * mm , (grid_height + 2*spacing) * mm , stroke=0 , fill=1)
            for row in card_positions:
                for i  in range(3):

                    if card_index < len(deck):
                        image_name = deck[card_index]['set_symbol'] + "-" + deck[card_index]['set_number']

                        if (deck[card_index]['two_sided'] and (conf['custom_backside'] or not conf['two_sided'] or working_on == 0)) and not do_B_side_next:
                            image_name += "_A"
                            if ((not conf['two_sided'] or conf['custom_backside']) and deck[card_index]['two_sided']):do_B_side_next = True
                        else: 
                            if (do_B_side_next or working_on) and deck[card_index]['two_sided']:
                                image_name += "_B"
                                do_B_side_next = False
                        if conf['custom_backside'] and working_on == 1:
                            image_name = conf['backside']
                            image_path = f"cardbacks/{conf['backside']}"
                        else:image_path = f"{image_folder}{image_name + image_format}"
                        
                        # Draw Rectangle (optional, for debugging/border)
                        #c.rect((grid_x_offset - spacing) * mm , (grid_y_offset - spacing) * mm , (grid_width + 2*spacing) * mm , (grid_height  + grid_x_offset + 2*spacing) * mm , stroke=0 ,  fill=1)

                        #c.setFillColorRGB(1, 1, 1) # White
                        #c.rect(x * mm, y * mm, rectangle_width * mm, rectangle_height * mm, stroke=1, fill=0)
                        
                        # --- Image Placement ---
                        if working_on == 0 or conf['custom_backside'] or deck[card_index]['two_sided']:
                            try:
                                
                                img = Image.open(image_path)
                                img_width, img_height = img.size
                                img.close()
                                
                                if conf['gamma_correction'] and working_on == 0:
                                     
                                    if correct_gamma(image_path,image_format):
                                        print(f"Gamma correction applied to {image_path}")
                                        image_path = image_path[:-4] + f"_gc{image_format}"
                                # --- debug pause ---
                                # --- Draw Grid of Images ---

                                # Calculate scaling factor (fit image within rectangle)
                                scale_x = (card_width * mm) / img_width
                                scale_y = (card_height * mm) / img_height
                                scale = min(scale_x, scale_y)

                                # Calculate centered image position
                                draw_width = img_width * scale
                                draw_height = img_height * scale
                                xindex = i
                                if conf['two_sided'] and working_on == 1: xindex = 2 - i
                                draw_x = row[xindex][0] * mm + (card_width * mm - draw_width) / 2
                                draw_y = row[i][1] * mm + (card_height * mm - draw_height) / 2

                                c.rect(draw_x - spacing * mm , draw_y - spacing * mm , draw_width + 2*spacing * mm , draw_height + 2*spacing * mm , stroke=0 , fill=1)
                                c.drawImage(image_path, draw_x, draw_y, width=draw_width, height=draw_height, mask='auto')
                                print(f"Placed {deck[card_index]['name']},{image_name}")
                            except Exception as e:

                                print(f"Error processing image {image_path}: {e}") # Handle image loading errors
                                raise e

                        # --- count up copy_counter if needed ---
                        if deck[card_index]['two_sided'] and (not conf['two_sided'] or conf['custom_backside']):
                            if working_on == 0 and not do_B_side_next:
                                copy_counter += 1
                        else:
                            copy_counter += 1
                        # --- count up card_index if needed ---
                        if copy_counter == deck[card_index]["copies"] : 
                            copy_counter = 0
                            card_index += 1
                            print(f"Card index: {image_path}")
            # Draw_reference_points
            if conf['reference_points']:
                for iterator_vectors in marker_iteration:
                    for vector in marker_vectors:
                        c.rect(grid_center_x + iterator_vectors[0] * grid_width * mm/2 , grid_center_y + iterator_vectors[1] * (grid_height + 10)*mm/2 , vector[0] , vector[1] , stroke=0 , fill=1)

            c.showPage()  # Move to the next page
        c.save()
        print(f"PDF created: {output_filename}")
        #if working_on == 1 or not conf['two_sided']: break
        working_on += 1


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

# two sided printing
two_sided:{conf['two_sided']}
# has custom backside
custom_backside:{conf['custom_backside']} 
# default backside image
backside:{conf['backside']}

# relative export path for pdf
pdf_path:{conf['pdf_path']}

# possible image types are small / normal / large / png / art_crop / border_crop
image_type:{conf['image_type']}

# default - for regular black border cards. Image size is 63x88 mm with 2 mm black spacing between cards
# bleed edge - for full art cards. Image size is 65x90.79 mm with no spacing between cards
mode:{conf['mode']}
# gamma correction for images
gamma_correction:{conf['gamma_correction']}
# toggle reference point True/False
reference_points:{conf['reference_points']}

# move everything on the x_axis
x_axis_offset:{conf['x_axis_offset']}

# user agent for scryfall bulk json download
user_agent:{conf['user_agent']}

# accept header for scryfall bulk json download
accept:{conf['accept']}
""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Default configuration values
    config = {
        'bulk_json_path' : '',
        'decklist_path' : 'decklist.txt',
        'two_sided': False,
        'custom_backside': False,
        'backside': 'back.png',
        'pdf_path' : 'output.pdf',
        'image_type' : 'png',
        'mode' : 'default',
        'gamma_correction' : True,
        'reference_points' : True,
        'x_axis_offset' : 0.75,
        'user_agent': 'decklist_to_pdf/0.1',
        'accept': 'application/json;q=0.9,*/*;q=0.8'
    }


    if not os.path.exists('decklist_to_pdf.ini'):
        write_config(config)

    logging.info("Loading configuration from decklist_to_pdf.ini")
    
    with open("decklist_to_pdf.ini", "r") as f:
        conf_count = 0
        for line in f:
            if line[0] == '#':
                continue
            parts = line.strip().split(':')
            match parts[0]:
                case 'bulk_json_path':
                    config['bulk_json_path'] = parts[1]
                    conf_count += 1
                case 'decklist_path':
                    config['decklist_path'] = parts[1]
                    conf_count += 1
                case 'backside':
                    config['backside'] = parts[1]
                    conf_count += 1
                case 'pdf_path':
                    config['pdf_path'] = parts[1]
                    conf_count += 1
                case 'image_type':
                    config['image_type'] = parts[1]
                    conf_count += 1
                case 'mode':
                    config['mode'] = parts[1]
                    conf_count += 1
                case 'gamma_correction':
                    config['gamma correction'] = parts[1] == 'True'
                    conf_count += 1
                case 'reference_points':
                    config['reference_points'] = parts[1] == 'True'
                    conf_count += 1
                case 'x_axis_offset':
                    config['x_axis_offset'] = parts[1]
                    conf_count += 1
                case 'two_sided':
                    config['two_sided'] = parts[1] == 'True'
                    conf_count += 1
                case 'custom_backside':
                    config['custom_backside'] = parts[1] == 'True'
                    conf_count += 1
                case 'user_agent':
                    config['user_agent'] = parts[1]
                    conf_count += 1
                case 'accept':
                    config['accept'] = parts[1]
                    conf_count += 1
        if conf_count < 13:
            logging.error("Old configu=ration file detected. Regenerating default config.")
            write_config(config)
        
    if not os.path.exists(config['bulk_json_path']):
        logging.info("No bulk json file found. Downloading...")
        config['bulk_json_path'] = fetch_bulk_json(config['user_agent'], config['accept'])
        write_config(config)

    logging.info(f"Loading Scryfall bulk json to dictionary from {config['bulk_json_path']}")
    card_dictionary = load_card_dictionary(config['bulk_json_path'])

    logging.info(f"Reading decklist from {config['decklist_path']}")
    deck_data = read_decklist(config['decklist_path'], card_dictionary)
    logging.info(f"Found {len(deck_data)} entries in decklist")

    logging.info("Checking image cache")
    create_image_cache(image_type=config['image_type'], card_data=card_dictionary, decklist=deck_data)

    logging.info("Creating PDF")

    create_grid_pdf(f"image_cache/{config['image_type']}/", "Output.pdf", deck_data, config)
