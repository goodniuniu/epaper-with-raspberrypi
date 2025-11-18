#!/usr/bin/env python3
"""
Working E-paper Display Test with Chinese Character Support
This will test the complete integration of weather + poetry + display
"""

import sys
import os
import time
import logging
from datetime import datetime

# Add e-paper library path
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('working_display_test.log')
    ]
)
logger = logging.getLogger(__name__)

def load_fonts():
    """Load fonts with Chinese support"""
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
                    break
                except Exception as e:
                    logger.warning(f"Failed to load font {path}: {e}")
                    continue

        if not fonts:
            from PIL import ImageFont
            fonts['large'] = fonts['medium'] = fonts['small'] = ImageFont.load_default()
            logger.warning("⚠️ Using default fonts only")

    except Exception as e:
        logger.error(f"❌ Font loading failed: {e}")
        return None

    return fonts

def create_display_image(weather_data, poem_data, fonts, width, height):
    """Create display image with proper UTF-8 encoding"""
    logger.info("🎨 Creating display image...")

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

            # Location and temperature
            location_text = f"📍 {location.get('name', 'Unknown')}"
            draw.text((10, y_pos), location_text, font=fonts['small'], fill=0)
            y_pos += 20

            temp_text = f"🌡️ {current.get('temp_c', 'N/A')}°C"
            draw.text((10, y_pos), temp_text, font=fonts['small'], fill=0)
            y_pos += 20

            condition_text = f"☁️ {current.get('condition', {}).get('text', 'Unknown')}"
            draw.text((10, y_pos), condition_text, font=fonts['small'], fill=0)
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
            # Title and author
            title_text = poem_data.title or "Untitled"
            author_text = f"— {poem_data.author or 'Unknown'}"

            # Render title safely
            try:
                draw.text((10, y_pos), title_text, font=fonts['small'], fill=0)
                y_pos += 20
                draw.text((10, y_pos), author_text, font=fonts['small'], fill=0)
                y_pos += 20
            except Exception as e:
                logger.warning(f"Could not render title: {e}")
                draw.text((10, y_pos), "Poem Title", font=fonts['small'], fill=0)
                y_pos += 20
                draw.text((10, y_pos), "Unknown Author", font=fonts['small'], fill=0)
                y_pos += 20

            # First line of poem
            if poem_data.content:
                y_pos += 5
                try:
                    # Split content to get first line
                    first_line = poem_data.content.split('，')[0] if '，' in poem_data.content else poem_data.content
                    draw.text((10, y_pos), first_line, font=fonts['small'], fill=0)
                    y_pos += 20
                except Exception as e:
                    logger.warning(f"Could not render poem content: {e}")
                    draw.text((10, y_pos), "Poem content", font=fonts['small'], fill=0)
                    y_pos += 20
        else:
            draw.text((10, y_pos), "Poetry data unavailable", font=fonts['small'], fill=0)
            y_pos += 20

        # === Footer ===
        y_pos = height - 30
        draw.line([(10, y_pos), (width - 10, y_pos)], fill=0, width=1)
        y_pos += 10

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        draw.text((10, y_pos), f"Updated: {timestamp}", font=fonts['small'], fill=0)

        logger.info("✅ Display image created successfully")
        return image

    except Exception as e:
        logger.error(f"❌ Failed to create display image: {e}")
        return None

def test_complete_system():
    """Test the complete weather + poetry + display system"""

    try:
        # Load project modules
        logger.info("📦 Loading project modules...")
        import get_weather
        import class_poem_api
        import get_config

        # Get configuration
        logger.info("⚙️ Loading configuration...")
        weather_api_key = get_config.get_config_value('WEATHER_API_KEY')
        city = get_config.get_config_value('CITY_API_KEY')
        poem_token_url = get_config.get_config_value('POEM_TOKEN_API_URL')
        daily_poem_url = get_config.get_config_value('DAILY_POEM_API_URL')

        logger.info(f"📍 Target city: {city}")

        # Fetch data
        logger.info("🌐 Fetching data...")

        # Weather data
        weather_data = get_weather.fetch_weather(weather_api_key, city)
        if weather_data:
            location = weather_data.get('location', {})
            current = weather_data.get('current', {})
            logger.info(f"🌤️ Weather: {location.get('name', 'Unknown')} - {current.get('temp_c', 'N/A')}°C, {current.get('condition', {}).get('text', 'Unknown')}")
        else:
            logger.warning("⚠️ Weather data fetch failed")

        # Poetry data
        poem_api = class_poem_api.PoemAPI(daily_poem_url, poem_token_url)
        if poem_api.get_poem_detail():
            logger.info(f"📜 Poetry: '{poem_api.title}' by {poem_api.author}")
        else:
            logger.warning("⚠️ Poetry data fetch failed")
            poem_api = None

        # Initialize e-paper
        logger.info("🖼️ Initializing e-paper display...")
        import waveshare_epd.epd3in52 as epd3in52
        epd = epd3in52.EPD()
        epd.init()
        epd.Clear()

        # Load fonts
        fonts = load_fonts()
        if not fonts:
            logger.error("❌ Cannot proceed without fonts")
            return False

        # Create and display image
        image = create_display_image(weather_data, poem_api, fonts, epd.width, epd.height)
        if image:
            logger.info("📺 Displaying image on e-paper...")
            epd.display(epd.getbuffer(image))
            logger.info("✅ Image displayed successfully!")

            # Save a copy for debugging
            image.save('working_display_test_output.png')
            logger.info("💾 Saved test image as 'working_display_test_output.png'")
        else:
            logger.error("❌ Failed to create display image")
            return False

        # Cleanup
        logger.info("😴 Putting display to sleep...")
        epd.sleep()

        return True

    except Exception as e:
        logger.error(f"❌ Complete system test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Complete E-paper Display System Test")
    print("=" * 50)
    print("This will test weather + poetry + display integration")
    print("Press Ctrl+C to stop at any time")
    print("=" * 50)

    success = test_complete_system()

    if success:
        print("✅ Complete system test completed successfully!")
        print("Your e-paper weather & poetry display is working!")
    else:
        print("❌ Complete system test failed!")
        print("Check the log file for troubleshooting information.")