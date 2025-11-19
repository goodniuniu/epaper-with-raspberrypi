#!/usr/bin/env python3
"""
Fixed E-paper Display Application with Proper Chinese Character Support
This version handles Chinese text encoding correctly
"""

import sys
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Add e-paper library path for hardware support
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fixed_display_app.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Global e-paper display instance
epd = None

def load_fonts():
    """Load fonts with proper Chinese character support"""
    fonts = {}

    try:
        # Try Chinese fonts first
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        for path in font_paths:
            if os.path.exists(path):
                try:
                    from PIL import ImageFont
                    fonts['large'] = ImageFont.truetype(path, 24)
                    fonts['medium'] = ImageFont.truetype(path, 18)
                    fonts['small'] = ImageFont.truetype(path, 12)
                    logger.info(f"✅ Loaded font: {path}")
                    return fonts
                except Exception as e:
                    logger.warning(f"Failed to load font {path}: {e}")
                    continue

        # Fallback to default fonts
        from PIL import ImageFont
        fonts['large'] = fonts['medium'] = fonts['small'] = ImageFont.load_default()
        logger.warning("⚠️ Using default fonts only")

    except Exception as e:
        logger.error(f"❌ Font loading failed: {e}")
        return None

    return fonts

def initialize_display():
    """Initialize e-paper display hardware"""
    global epd

    try:
        logger.info("🖼️ Initializing e-paper display...")
        import waveshare_epd.epd3in52 as epd3in52
        epd = epd3in52.EPD()
        epd.init()
        epd.Clear()
        logger.info("✅ E-paper display initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize display: {e}")
        return False

def render_chinese_text_safely(draw, text, x, y, font, fallback_text=None):
    """Safely render Chinese text with encoding fallback"""
    try:
        # Try to render the text directly
        if text and text.strip():
            draw.text((x, y), text.strip(), font=font, fill=0)
            return True
    except (UnicodeEncodeError, UnicodeError) as e:
        logger.warning(f"⚠️ Cannot render Chinese text '{text}': {e}")

        # Fallback to ASCII or provided fallback text
        if fallback_text:
            try:
                draw.text((x, y), fallback_text, font=font, fill=0)
                return True
            except:
                pass

        # Ultimate fallback
        try:
            ascii_text = text.encode('ascii', errors='replace').decode('ascii')
            draw.text((x, y), ascii_text, font=font, fill=0)
            return True
        except:
            return False

    return False

def create_display_image(weather_data, poem_data, fonts, width, height):
    """Create display image with weather and poetry data (encoding-safe)"""
    try:
        from PIL import Image, ImageDraw

        # Create image
        image = Image.new('1', (width, height), 255)  # White background
        draw = ImageDraw.Draw(image)

        y_pos = 10

        # === Header ===
        render_chinese_text_safely(draw, "Weather & Poetry Display", 10, y_pos, fonts['large'])
        y_pos += 35
        draw.line([(10, y_pos), (width - 10, y_pos)], fill=0, width=1)
        y_pos += 15

        # === Weather Section ===
        render_chinese_text_safely(draw, "Current Weather:", 10, y_pos, fonts['medium'])
        y_pos += 25

        if weather_data:
            location = weather_data.get('location', {})
            current = weather_data.get('current', {})

            # Location
            location_text = f"📍 {location.get('name', 'Unknown')}"
            render_chinese_text_safely(draw, location_text, 10, y_pos, fonts['small'])
            y_pos += 20

            # Temperature
            temp_text = f"🌡️ {current.get('temp_c', 'N/A')}°C"
            render_chinese_text_safely(draw, temp_text, 10, y_pos, fonts['small'])
            y_pos += 20

            # Weather condition
            condition_text = f"☁️ {current.get('condition', {}).get('text', 'Unknown')}"
            render_chinese_text_safely(draw, condition_text, 10, y_pos, fonts['small'])
            y_pos += 20

            # Humidity
            humidity_text = f"💧 {current.get('humidity', 'N/A')}% humidity"
            render_chinese_text_safely(draw, humidity_text, 10, y_pos, fonts['small'])
            y_pos += 20
        else:
            render_chinese_text_safely(draw, "Weather data unavailable", 10, y_pos, fonts['small'])
            y_pos += 20

        y_pos += 10
        draw.line([(10, y_pos), (width - 10, y_pos)], fill=0, width=1)
        y_pos += 15

        # === Poetry Section ===
        render_chinese_text_safely(draw, "Today's Poetry:", 10, y_pos, fonts['medium'])
        y_pos += 25

        if poem_data:
            # Title and dynasty (with fallback)
            title = poem_data.title or "Untitled"
            dynasty = poem_data.dynasty or "Unknown Dynasty"

            if render_chinese_text_safely(draw, title, 10, y_pos, fonts['small'], f"Poem: {len(title)} chars"):
                y_pos += 20

            if render_chinese_text_safely(draw, f"({dynasty})", 10, y_pos, fonts['small'], f"Dynasty: {dynasty}"):
                y_pos += 20

            # Author
            author_text = f"— {poem_data.author or 'Unknown Author'}"
            if render_chinese_text_safely(draw, author_text, 10, y_pos, fonts['small'], f"Author: {poem_data.author or 'Unknown'}"):
                y_pos += 20

            # First lines of poem
            if poem_data.content:
                y_pos += 5
                try:
                    # Split content and show first few lines
                    lines = poem_data.content.split('，')
                    for i, line in enumerate(lines[:3]):  # Show max 3 lines
                        if line.strip():
                            text_with_punctuation = line.strip() + ('，' if i < len(lines)-1 and i < 2 else '')
                            if not render_chinese_text_safely(draw, text_with_punctuation, 10, y_pos, fonts['small'], f"Line {i+1}"):
                                # Show line number if Chinese text fails
                                draw.text((10, y_pos), f"Poem line {i+1}", font=fonts['small'], fill=0)
                            y_pos += 20
                            if y_pos > height - 80:  # Prevent overflow
                                break
                except Exception as e:
                    logger.warning(f"Could not process poem content: {e}")
                    render_chinese_text_safely(draw, "Poem content unavailable", 10, y_pos, fonts['small'])
        else:
            render_chinese_text_safely(draw, "Poetry data unavailable", 10, y_pos, fonts['small'])
            y_pos += 20

        # === Footer ===
        y_pos = height - 30
        draw.line([(10, y_pos), (width - 10, y_pos)], fill=0, width=1)
        y_pos += 10

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        render_chinese_text_safely(draw, f"Updated: {timestamp}", 10, y_pos, fonts['small'])

        return image

    except Exception as e:
        logger.error(f"❌ Failed to create display image: {e}")
        return None

def display_on_epaper(image):
    """Display image on e-paper screen"""
    global epd

    if not epd or not image:
        logger.error("❌ Cannot display: display not initialized or no image")
        return False

    try:
        logger.info("📺 Displaying image on e-paper...")
        epd.display(epd.getbuffer(image))
        logger.info("✅ Image displayed successfully!")

        # Save a copy for debugging
        image.save('fixed_current_display.png')
        logger.info("💾 Display image saved as 'fixed_current_display.png'")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to display image: {e}")
        return False

def cleanup_display():
    """Clean up and put display to sleep"""
    global epd

    if epd:
        try:
            logger.info("😴 Putting display to sleep...")
            epd.sleep()
            logger.info("✅ Display put to sleep successfully")
        except Exception as e:
            logger.error(f"❌ Error putting display to sleep: {e}")

def fetch_weather_data(weather_api_key: str, city: str) -> Optional[Dict[str, Any]]:
    """Fetch weather data from the API."""
    try:
        import get_weather
        weather = get_weather.fetch_weather(weather_api_key, city)
        return weather
    except Exception as e:
        logger.error(f"Failed to fetch weather data: {e}")
        return None

def fetch_poem_data(token_url: str, daily_poem_url: str) -> Optional['class_poem_api.PoemAPI']:
    """Fetch poem data using the PoemAPI class."""
    try:
        import class_poem_api
        poem_api = class_poem_api.PoemAPI(daily_poem_url, token_url)
        if poem_api.get_poem_detail():
            return poem_api
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to fetch poem data: {e}")
        return None

def main() -> None:
    """Main application entry point."""
    logger.info("Starting Fixed E-paper Display Application")

    try:
        # Load configuration
        import get_config
        weather_api_key = get_config.get_config_value('WEATHER_API_KEY')
        city_api_key = get_config.get_config_value('CITY_API_KEY')
        poem_token_api_url = get_config.get_config_value('POEM_TOKEN_API_URL')
        daily_poem_api_url = get_config.get_config_value('DAILY_POEM_API_URL')

        logger.info(f"Configuration loaded. Target city: {city_api_key}")

        # Initialize display
        if not initialize_display():
            logger.error("❌ Failed to initialize display. Exiting.")
            return

        # Load fonts
        fonts = load_fonts()
        if not fonts:
            logger.error("❌ Failed to load fonts. Cannot create display.")
            return

        # Fetch weather data
        weather = fetch_weather_data(weather_api_key, city_api_key)
        if weather:
            logger.info("Weather data retrieved successfully:")
            location = weather.get('location', {})
            current = weather.get('current', {})
            logger.info(f"Current temperature: {current.get('temp_c', 'N/A')}°C")
            logger.info(f"Condition: {current.get('condition', {}).get('text', 'N/A')}")
            logger.info(f"Location: {location.get('name', 'N/A')}")
        else:
            logger.warning("No weather data available")

        # Fetch poem data
        poem_api = fetch_poem_data(poem_token_api_url, daily_poem_api_url)
        if poem_api:
            logger.info("Poem data retrieved successfully:")
            logger.info(f"Title: {poem_api.title or 'N/A'}")
            logger.info(f"Dynasty: {poem_api.dynasty or 'N/A'}")
            logger.info(f"Author: {poem_api.author or 'N/A'}")
            logger.info(f"Content preview: {poem_api.content or 'N/A'}")
        else:
            logger.warning("No poem data available")

        # Create and display on e-paper
        image = create_display_image(weather, poem_api, fonts, epd.width, epd.height)
        if image:
            display_on_epaper(image)
        else:
            logger.error("❌ Failed to create display image")

        logger.info("Application completed successfully")

    except Exception as e:
        logger.error(f"Application failed: {e}")
        raise

    finally:
        # Always cleanup the display
        cleanup_display()

if __name__ == '__main__':
    main()