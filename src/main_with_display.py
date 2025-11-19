#!/usr/bin/env python3
"""
Modern E-paper Display Application with Display Support
Updated: 2025-11-18

Main application for fetching weather and Chinese poetry data
for display on Raspberry Pi e-paper screen.
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
        logging.FileHandler('epaper_app.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Global e-paper display instance
epd = None

def load_fonts():
    """Load fonts with Chinese character support"""
    fonts = {}

    try:
        from PIL import ImageFont
        logger.info("🔍 Searching for available fonts...")

        # Try working version font first (which works for both English and Chinese)
        font_paths = [
            "/home/admin/Downloads/e-Paper/RaspberryPi_JetsonNano/python/pic/Font.ttc",  # Working version font
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Try microhei first (usually more stable)
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Fallback for English only
        ]

        for i, path in enumerate(font_paths):
            logger.info(f"🔍 Trying font {i+1}/{len(font_paths)}: {path}")

            if os.path.exists(path):
                try:
                    logger.info(f"📁 Font file exists, attempting to load...")
                    fonts['large'] = ImageFont.truetype(path, 24)
                    fonts['medium'] = ImageFont.truetype(path, 18)
                    fonts['small'] = ImageFont.truetype(path, 12)
                    logger.info(f"✅ Successfully loaded font: {path}")

                    # Test if font can render both English and Chinese characters
                    test_text_en = "Test English"
                    test_text_cn = "测试中文"

                    # Test English rendering
                    try:
                        test_size_en = fonts['medium'].getlength(test_text_en)
                        logger.info(f"📏 English test: '{test_text_en}' renders at {test_size_en:.1f} pixels")
                    except Exception as e:
                        logger.warning(f"⚠️ English rendering test failed: {e}")

                    # Test Chinese rendering
                    try:
                        test_size_cn = fonts['medium'].getlength(test_text_cn)
                        logger.info(f"📏 Chinese test: '{test_text_cn}' renders at {test_size_cn:.1f} pixels")
                    except Exception as e:
                        logger.warning(f"⚠️ Chinese rendering test failed: {e}")
                        logger.warning(f"⚠️ This font may not support Chinese characters properly")
                        continue  # Skip this font and try the next one

                    return fonts

                except Exception as e:
                    logger.warning(f"❌ Failed to load font {path}: {e}")
                    continue
            else:
                logger.warning(f"⚠️ Font file not found: {path}")

        # Fallback to default fonts
        logger.warning("⚠️ No TrueType fonts worked, using default fonts")
        fonts['large'] = fonts['medium'] = fonts['small'] = ImageFont.load_default()
        logger.info("✅ Default fonts loaded")

    except Exception as e:
        logger.error(f"❌ Font loading failed: {e}")
        return None

    return fonts

def initialize_display():
    """Initialize e-paper display hardware using working method"""
    global epd

    try:
        logger.info("🖼️ Initializing e-paper display using working method...")

        # Use the working version import method
        from waveshare_epd import epd3in52
        epd = epd3in52.EPD()

        # Use the working version initialization sequence
        epd.init()
        epd.display_NUM(epd.WHITE)  # Use working method instead of Clear()
        epd.lut_GC()                # Load lookup table
        epd.refresh()               # Manual refresh

        # Additional initialization from working version
        epd.send_command(0x50)
        epd.send_data(0x17)

        logger.info("✅ E-paper display initialized successfully using working method")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize display: {e}")
        return False

def create_display_image(weather_data, poem_data, fonts, width, height):
    """Create display image with weather and poetry data"""
    try:
        from PIL import Image, ImageDraw

        # Create image
        image = Image.new('1', (width, height), 255)  # White background
        draw = ImageDraw.Draw(image)

        y_pos = 10

        # === Header ===
        draw.text((10, y_pos), "Weather & Poetry Display", font=fonts['large'], fill=0)
        y_pos += 35
        draw.line([(10, y_pos), (width - 10, y_pos)], fill=0, width=1)
        y_pos += 15

        # === Weather Section ===
        draw.text((10, y_pos), "Current Weather:", font=fonts['medium'], fill=0)
        y_pos += 25

        if weather_data:
            location = weather_data.get('location', {})
            current = weather_data.get('current', {})

            # Location
            location_text = f"{location.get('name', 'Unknown')}"
            draw.text((10, y_pos), location_text, font=fonts['small'], fill=0)
            y_pos += 20

            # Temperature
            temp_text = f"Temp: {current.get('temp_c', 'N/A')}C"
            draw.text((10, y_pos), temp_text, font=fonts['small'], fill=0)
            y_pos += 20

            # Weather condition
            condition_text = f"Weather: {current.get('condition', {}).get('text', 'Unknown')}"
            draw.text((10, y_pos), condition_text, font=fonts['small'], fill=0)
            y_pos += 20

            # Humidity
            humidity_text = f"Humidity: {current.get('humidity', 'N/A')}%"
            draw.text((10, y_pos), humidity_text, font=fonts['small'], fill=0)
            y_pos += 20
        else:
            draw.text((10, y_pos), "Weather data unavailable", font=fonts['small'], fill=0)
            y_pos += 20

        y_pos += 10
        draw.line([(10, y_pos), (width - 10, y_pos)], fill=0, width=1)
        y_pos += 15

        # === Poetry Section ===
        draw.text((10, y_pos), "Today's Poetry:", font=fonts['medium'], fill=0)
        y_pos += 25

        if poem_data:
            # Title and dynasty
            title_text = poem_data.title or "Untitled"
            dynasty_text = poem_data.dynasty or "Unknown Dynasty"

            try:
                draw.text((10, y_pos), title_text, font=fonts['small'], fill=0)
                y_pos += 20
                draw.text((10, y_pos), f"({dynasty_text})", font=fonts['small'], fill=0)
                y_pos += 20
            except Exception as e:
                logger.warning(f"Could not render title: {e}")
                draw.text((10, y_pos), "Poem Title", font=fonts['small'], fill=0)
                y_pos += 40

            # Author
            author_text = f"— {poem_data.author or 'Unknown Author'}"
            try:
                draw.text((10, y_pos), author_text, font=fonts['small'], fill=0)
                y_pos += 20
            except Exception as e:
                logger.warning(f"Could not render author: {e}")
                draw.text((10, y_pos), "Unknown Author", font=fonts['small'], fill=0)
                y_pos += 20

            # First lines of poem
            if poem_data.content:
                y_pos += 5
                try:
                    logger.info(f"🎨 Attempting to render poem content: '{poem_data.content[:50]}...'")
                    # Split content and show first few lines
                    lines = poem_data.content.split('，')
                    for i, line in enumerate(lines[:3]):  # Show max 3 lines
                        if line.strip():
                            text_to_render = line.strip() + ('，' if i < len(lines)-1 and i < 2 else '')
                            logger.info(f"🎨 Rendering line {i+1}: '{text_to_render}'")
                            draw.text((10, y_pos), text_to_render, font=fonts['small'], fill=0)
                            y_pos += 20
                            if y_pos > height - 80:  # Prevent overflow
                                break
                except Exception as e:
                    logger.warning(f"Could not render poem content: {e}")
                    # Fallback to English message if Chinese rendering fails
                    try:
                        draw.text((10, y_pos), "Poem content display error", font=fonts['small'], fill=0)
                    except Exception as e2:
                        logger.error(f"Even fallback text failed: {e2}")
                        from PIL import ImageFont
                        draw.text((10, y_pos), "Poem error", font=ImageFont.load_default(), fill=0)
        else:
            draw.text((10, y_pos), "Poetry data unavailable", font=fonts['small'], fill=0)
            y_pos += 20

        # === Footer ===
        y_pos = height - 30
        draw.line([(10, y_pos), (width - 10, y_pos)], fill=0, width=1)
        y_pos += 10

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        draw.text((10, y_pos), f"Updated: {timestamp}", font=fonts['small'], fill=0)

        return image

    except Exception as e:
        logger.error(f"❌ Failed to create display image: {e}")
        return None

def display_on_epaper(image):
    """Display image on e-paper screen using working method"""
    global epd

    if not epd or not image:
        logger.error("❌ Cannot display: display not initialized or no image")
        return False

    try:
        logger.info("📺 Displaying image on e-paper using working method...")

        # Use the working version display sequence
        epd.display(epd.getbuffer(image))
        epd.lut_GC()    # Load lookup table after display
        epd.refresh()   # Manual refresh

        logger.info("✅ Image displayed successfully using working method!")

        # Save a copy for debugging
        image.save('current_display.png')
        logger.info("💾 Display image saved as 'current_display.png'")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to display image: {e}")
        return False

def cleanup_display():
    """Clean up and put display to sleep using working method"""
    global epd

    if epd:
        try:
            logger.info("😴 Putting display to sleep using working method...")
            epd.sleep()
            logger.info("✅ Display put to sleep successfully")

            # Use the working version cleanup method
            from waveshare_epd import epd3in52
            epd3in52.epdconfig.module_exit(cleanup=True)
            logger.info("✅ GPIO cleanup completed")
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
    logger.info("Starting E-paper Display Application")

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
            logger.error("❌ Failed to initialize display. Continuing in console mode only.")

        # Load fonts
        fonts = load_fonts()
        if not fonts:
            logger.error("❌ Failed to load fonts. Cannot create display.")

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

        # Create and display on e-paper if available
        if epd and fonts:
            image = create_display_image(weather, poem_api, fonts, epd.width, epd.height)
            if image:
                display_on_epaper(image)
            else:
                logger.error("❌ Failed to create display image")
        else:
            logger.info("📱 Display mode: Console only (e-paper display not available)")

        logger.info("Application completed successfully")

    except Exception as e:
        logger.error(f"Application failed: {e}")
        raise

    finally:
        # Always cleanup the display
        cleanup_display()

if __name__ == '__main__':
    main()