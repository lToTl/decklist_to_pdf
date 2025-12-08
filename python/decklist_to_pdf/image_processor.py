"""
Decklist to PDF - Image Processing

Handles image downloading, caching, resizing, and gamma correction.
"""
import io
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep, perf_counter

import requests
from PIL import Image, ImageEnhance

from .models import (
    Config,
    GAMMA_THRESHOLD,
    MAX_GAMMA,
    BORDER_SAMPLE_OFFSET,
    RETRY_COUNT,
    RATE_LIMIT_DELAY,
)


class ImageProcessor:
    """Handles all image operations: downloading, caching, resizing, and gamma correction."""
    
    def __init__(self, config: Config, card_width_px: int, card_height_px: int, image_format: str):
        """
        Initialize the image processor.
        
        Args:
            config: Configuration object
            card_width_px: Card width in pixels at target DPI
            card_height_px: Card height in pixels at target DPI
            image_format: Image format (png or jpg)
        """
        self.config = config
        self.card_width_px = card_width_px
        self.card_height_px = card_height_px
        self.image_format = image_format
        self.headers = {
            'User-Agent': config.user_agent,
            'Accept': config.accept
        }
        self.image_cache: dict[str, Image.Image] = {}
    
    def create_cache(self, decklist: list[dict]) -> dict[str, Image.Image]:
        """
        Download and cache all images needed for the decklist.
        
        Args:
            decklist: List of decklist entries
            
        Returns:
            Dictionary mapping card keys to PIL Image objects
        """
        self._ensure_directories()
        
        timer_start = perf_counter()
        futures = []
        download_count = 0
        processed_keys = set()
        
        with ThreadPoolExecutor(self.config.worker_threads) as executor:
            for entry in decklist:
                if 'sides' not in entry or entry['sides'] is None:
                    continue
                    
                for side in entry['sides']:
                    key = side.get('key')
                    if key == 'back' or key in processed_keys:
                        continue
                    
                    processed_keys.add(key)
                    
                    if side.get('custom', False):
                        # Custom card
                        source = f"custom_cards/{side['name']}.png"
                        dest = f"custom_cards/{side['name']}.{self.image_format}"
                        futures.append(executor.submit(
                            self._fetch_image, source, dest, key, is_custom=True, black_bordered=False
                        ))
                    else:
                        # Scryfall card
                        image_uri = side['image_uris'][self.config.image_type]
                        dest = f"image_cache/{self.config.image_type}/{key}.{self.image_format}"
                        
                        if not os.path.exists(dest):
                            download_count += 1
                            sleep(RATE_LIMIT_DELAY)
                        
                        futures.append(executor.submit(
                            self._fetch_image, image_uri, dest, key, is_custom=False, black_bordered=side.get('black_bordered', False)
                        ))
            
            # Handle custom backside
            if self.config.custom_backside and self.config.two_sided:
                backside_path = f"cardbacks/{self.config.backside}"
                if os.path.exists(backside_path):
                    futures.append(executor.submit(
                        self._fetch_image, backside_path, backside_path, "back", is_custom=True, black_bordered=False
                    ))
            
            # Wait for all downloads to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error in image processing: {e}")
                    executor.shutdown(wait=False, cancel_futures=True)
                    raise
        
        timer_end = perf_counter()
        logging.info(f"Downloaded {download_count} new images")
        logging.info(f"Image cache created in {timer_end - timer_start:.2f} seconds")
        
        return self.image_cache
    
    def _ensure_directories(self) -> None:
        """Create necessary cache directories."""
        image_type = self.config.image_type
        dpi = self.config.dpi
        
        os.makedirs(f"image_cache/{image_type}", exist_ok=True)
        os.makedirs(f"image_cache/{dpi}/{image_type}", exist_ok=True)
        os.makedirs(f"custom_cards/{dpi}", exist_ok=True)
        os.makedirs(f"cardbacks/{dpi}", exist_ok=True)
    
    def _fetch_image(self, source: str, destination: str, key: str, is_custom: bool, black_bordered: bool) -> None:
        """
        Fetch, process, and cache an image.
        
        Args:
            source: URL or local path to source image
            destination: Path to save the image
            key: Cache key for the image
            is_custom: Whether this is a custom card
        """
        retries = RETRY_COUNT
        img = Image.new('RGB', (1, 1), color=(255, 255, 255))
        
        # Calculate DPI-scaled paths
        if is_custom:
            parts = destination.split('/')
            dpi_destination = f"{parts[0]}/{self.config.dpi}/{parts[1]}"
        else:
            parts = destination.split('/')
            dpi_destination = f"{parts[0]}/{self.config.dpi}/{parts[1]}/{parts[2]}"
        
        gc_path = dpi_destination[:-4] + f"_gc{os.path.splitext(dpi_destination)[1]}"
        
        # Custom cards: simpler path without gamma correction
        if is_custom:
            img = self._process_custom_image(source, dpi_destination, retries)
            self.image_cache[key] = img
            return
        
        # Standard cards: check cache hierarchy
        if os.path.exists(gc_path) and self.config.gamma_correction and black_bordered:
            img = self._open_image(gc_path, retries)
        elif os.path.exists(dpi_destination):
            img = self._open_image(dpi_destination, retries)
            if self.config.gamma_correction and black_bordered:
                img = self._apply_gamma_correction(img, gc_path, retries)
        elif os.path.exists(destination):
            img = self._open_image(destination, retries)
            img = self._resize_image(img, dpi_destination)
            if self.config.gamma_correction:
                img = self._apply_gamma_correction(img, gc_path, retries)
        else:
            img = self._download_image(source, destination, retries)
            img = self._resize_image(img, dpi_destination)
            if self.config.gamma_correction and black_bordered:
                img = self._apply_gamma_correction(img, gc_path, retries)
        
        self.image_cache[key] = img
    
    def _process_custom_image(self, source: str, dpi_destination: str, retries: int) -> Image.Image:
        """Process a custom card image."""
        if os.path.exists(dpi_destination):
            return self._open_image(dpi_destination, retries)
        
        img = self._open_image(source, retries)
        return self._resize_image(img, dpi_destination)
    
    def _download_image(self, url: str, destination: str, retries: int) -> Image.Image:
        """Download an image from URL."""
        if url is None:
            raise ValueError(f"Image URL is None for destination {destination}")
        
        while retries > 0:
            try:
                logging.info(f"Downloading image {destination}")
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                
                img = Image.open(io.BytesIO(response.content))
                img.save(destination, self.image_format)
                img.load()
                return img
                
            except Exception as e:
                retries -= 1
                logging.error(f"Error downloading {url}: {e}")
                if retries > 0:
                    logging.info(f"Retrying ({retries} left)")
                    sleep(1)
                else:
                    raise
        
        raise RuntimeError(f"Failed to download {url}")
    
    def _open_image(self, path: str, retries: int) -> Image.Image:
        """Open an image from disk."""
        while retries > 0:
            try:
                with Image.open(path) as opened_img:
                    opened_img.load()
                    return opened_img.copy()
            except Exception as e:
                retries -= 1
                logging.error(f"Error opening {path}: {e}")
                if retries > 0:
                    sleep(0.1)
                else:
                    raise
        
        raise RuntimeError(f"Failed to open {path}")
    
    def _resize_image(self, img: Image.Image, destination: str) -> Image.Image:
        """Resize image to card dimensions and save."""
        resized = img.resize(
            (self.card_width_px, self.card_height_px),
            Image.Resampling.LANCZOS
        ).convert("RGB")
        
        resized.save(destination, self.image_format)
        resized.load()
        return resized
    
    def _apply_gamma_correction(self, img: Image.Image, gc_path: str, retries: int) -> Image.Image:
        """
        Apply gamma correction to make dark borders truly black.
        
        This improves print quality by adjusting the contrast so that
        card borders are pure black rather than dark gray.
        """
        try:
            width, height = img.size
            if width == 0 or height == 0:
                raise ValueError("Image has zero dimensions")
            
            # Sample border color from bottom edge
            sample_y = int(height - height * BORDER_SAMPLE_OFFSET)
            border_color = img.getpixel((width // 2, sample_y))
            
            if border_color is None:
                raise ValueError("Could not sample border color")
            
            # Calculate average brightness
            if isinstance(border_color, (tuple, list)):
                border_gamma = sum(border_color[:3]) / 3
            elif isinstance(border_color, (int, float)):
                border_gamma = border_color
            else:
                raise ValueError(f"Unknown color format: {type(border_color)}")
            
            # Skip if border is too bright (likely not a black border card)
            if border_gamma > MAX_GAMMA:
                logging.warning(f"Border too bright ({border_gamma}), skipping gamma correction")
                return img
            
            # Iteratively increase contrast until border is black
            while border_gamma > GAMMA_THRESHOLD:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1 + border_gamma / 256)
                
                try:
                    border_color = img.getpixel((width // 2, sample_y))
                except IndexError:
                    break
                
                if isinstance(border_color, (tuple, list)):
                    border_gamma = sum(border_color[:3]) / 3 if len(border_color) >= 3 else border_color[0]
                elif isinstance(border_color, (int, float)):
                    border_gamma = border_color
                else:
                    break
            
            img.save(gc_path)
            img.load()
            logging.info(f"Gamma correction applied, saved to {gc_path}")
            return img
            
        except Exception as e:
            logging.error(f"Error applying gamma correction: {e}")
            if retries > 0:
                return img  # Return uncorrected image
            raise


def resize_image_to_card_size(image: Image.Image, card_width_px: int, card_height_px: int) -> Image.Image:
    """
    Resize an image to the target card size.
    
    Args:
        image: PIL Image object
        card_width_px: Target width in pixels
        card_height_px: Target height in pixels
        
    Returns:
        Resized PIL Image object in RGB mode
    """
    return image.resize(
        (card_width_px, card_height_px),
        Image.Resampling.LANCZOS
    ).convert("RGB")
