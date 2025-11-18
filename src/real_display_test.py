#!/usr/bin/env python3
"""
Real E-Paper Display Test
Safely tests the actual connected e-paper hardware

This script will:
1. Test hardware initialization
2. Display weather and poetry data
3. Handle errors gracefully
4. Clean up properly
"""

import os
import sys
import time
import logging
import signal
from typing import Optional
from datetime import datetime

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
libdir = os.path.join(project_root, 'lib')
picdir = os.path.join(project_root, 'pic')

if os.path.exists(libdir):
    sys.path.append(libdir)
if os.path.exists(picdir):
    sys.path.append(picdir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('real_display_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Global flag for cleanup
epd = None

def cleanup_and_exit(signum=None, frame=None):
    """Cleanup function for graceful shutdown"""
    global epd
    logger.info("🧹 Cleaning up...")

    try:
        if epd:
            epd.sleep()
            logger.info("✅ E-paper display put to sleep")
    except Exception as e:
        logger.warning(f"⚠️ Cleanup warning: {e}")

    logger.info("👋 Exiting gracefully")
    sys.exit(0)

# Register cleanup for various exit signals
signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)

def test_hardware_initialization():
    """Test e-paper hardware initialization"""
    logger.info("🔧 Testing e-paper hardware initialization...")

    try:
        # Try to import Waveshare e-paper library
        from waveshare_epd import epd3in52
        logger.info("✅ Waveshare e-paper library imported successfully")
    except ImportError as e:
        logger.error(f"❌ Cannot import e-paper library: {e}")
        logger.info("💡 Install instructions:")
        logger.info("   cd ~/ && git clone https://github.com/waveshare/e-Paper.git")
        logger.info("   cd e-Paper/RaspberryPi_JetsonNano/python/lib")
        logger.info("   pip install -r requirements.txt")
        return None

    try:
        # Initialize the e-paper display
        epd_instance = epd3in52.EPD()
        logger.info("🖼️ EPD 3.52-inch driver object created")

        # Initialize the hardware
        epd_instance.init()
        logger.info("✅ E-paper hardware initialized successfully")

        # Clear the screen
        epd_instance.Clear()
        logger.info("✅ E-paper screen cleared")

        return epd_instance

    except Exception as e:
        logger.error(f"❌ Hardware initialization failed: {e}")
        logger.info("💡 Possible issues:")
        logger.info("   - Display not properly connected")
        logger.info("   - I2C/SPI not enabled")
        logger.info("   - GPIO permissions issue")
        logger.info("   - Wrong e-paper model (3.52' expected)")
        return None

def load_dependencies():
    """Load required dependencies and APIs"""
    logger.info("📦 Loading dependencies...")

    try:
        # Add src directory to path
        src_dir = os.path.dirname(os.path.abspath(__file__))
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        # Import our modules
        import get_config
        import get_weather
        import class_poem_api

        logger.info("✅ All application modules imported")
        return get_config, get_weather, class_poem_api

    except Exception as e:
        logger.error(f"❌ Failed to load dependencies: {e}")
        return None, None, None

def get_fonts():
    """Load fonts for display"""
    logger.info("🔤 Loading fonts...")

    fonts = {}

    try:
        # Try system fonts first with Chinese support
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Chinese font
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Chinese font
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]

        # Look for fonts
        for i, path in enumerate(font_paths):
            if os.path.exists(path):
                try:
                    if i == 0:
                        fonts['large'] = fonts.get('large', ImageFont.truetype(path, 24))
                    fonts['medium'] = ImageFont.truetype(path, 18)
                    fonts['small'] = ImageFont.truetype(path, 12)
                    logger.info(f"✅ Loaded font: {i+1}")
                except:
                    continue

        # Fallback to default fonts
        if not fonts:
            from PIL import ImageFont
            fonts['large'] = fonts['medium'] = fonts['small'] = ImageFont.load_default()
            logger.warning("⚠️ Using default fonts only")

        return fonts

    except Exception as e:
        logger.warning(f"⚠️ Font loading issue: {e}")

        # Emergency fallback
        try:
            from PIL import ImageFont
            default_font = ImageFont.load_default()
            return {'large': default_font, 'medium': default_font, 'small': default_font}
        except:
            logger.error("❌ Cannot load any fonts")
            return None

def fetch_display_data(get_config, get_weather, class_poem_api):
    """Fetch weather and poetry data"""
    logger.info("🌐 Fetching display data...")

    try:
        # Load configuration
        weather_api_key = get_config.get_config_value('WEATHER_API_KEY')
        city_api_key = get_config.get_config_value('CITY_API_KEY')
        poem_token_url = get_config.get_config_value('POEM_TOKEN_API_URL')
        daily_poem_url = get_config.get_config_value('DAILY_POEM_API_URL')

        logger.info(f"📍 Target city: {city_api_key}")

        # Fetch weather data
        weather_data = get_weather.fetch_weather(weather_api_key, city_api_key)
        if weather_data:
            location = weather_data.get('location', {}).get('name', 'Unknown')
            temp = weather_data.get('current', {}).get('temp_c', 'N/A')
            condition = weather_data.get('current', {}).get('condition', {}).get('text', 'N/A')
            logger.info(f"🌤️ Weather: {location} - {temp}°C, {condition}")
        else:
            logger.warning("⚠️ Weather data not available")

        # Fetch poetry data
        poem_api = class_poem_api.PoemAPI(daily_poem_url, poem_token_url)
        if poem_api.get_poem_detail():
            title = poem_api.title or "Unknown"
            author = poem_api.author or "Unknown"
            logger.info(f"📜 Poetry: '{title}' by {author}")
        else:
            logger.warning("⚠️ Poetry data not available")

        return weather_data, poem_api

    except Exception as e:
        logger.error(f"❌ Data fetching failed: {e}")
        return None, None

def create_display_image(weather_data, poem_data, fonts, epd_instance):
    """Create display image and render to e-paper"""
    logger.info("🎨 Creating display image...")

    try:
        from PIL import Image, ImageDraw
        import get_ipaddress

        # Create image
        width, height = epd_instance.width, epd_instance.height
        image = Image.new('1', (width, height), 255)
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
            location_name = location.get('name', 'Unknown')
            draw.text((10, y_pos), f"Location: {location_name}", font=fonts['medium'], fill=0)
            y_pos += 25

            # Temperature
            temp = current.get('temp_c', 'N/A')
            draw.text((10, y_pos), f"Temperature: {temp}°C", font=fonts['medium'], fill=0)
            y_pos += 25

            # Condition
            condition = current.get('condition', {}).get('text', 'N/A')
            draw.text((10, y_pos), f"Condition: {condition}", font=fonts['medium'], fill=0)
            y_pos += 25

            # Additional info
            humidity = current.get('humidity', 'N/A')
            draw.text((10, y_pos), f"Humidity: {humidity}%", font=fonts['small'], fill=0)
            y_pos += 35
        else:
            draw.text((10, y_pos), "Weather data unavailable", font=fonts['medium'], fill=0)
            y_pos += 35

        # Separator
        draw.line([(10, y_pos), (width - 10, y_pos)], fill=0, width=1)
        y_pos += 15

        # === Poetry Section ===
        draw.text((10, y_pos), "Today's Poetry:", font=fonts['medium'], fill=0)
        y_pos += 25

        if poem_data:
            # Title
            title = poem_data.title or "Untitled"
            draw.text((10, y_pos), f"Title: {title}", font=fonts['medium'], fill=0)
            y_pos += 25

            # Dynasty and author
            dynasty = poem_data.dynasty or "Unknown"
            author = poem_data.author or "Unknown"
            draw.text((10, y_pos), f"Dynasty: {dynasty} | Author: {author}", font=fonts['medium'], fill=0)
            y_pos += 30

            # Content preview
            content = poem_data.content or "No content"
            draw.text((10, y_pos), "Preview:", font=fonts['medium'], fill=0)
            y_pos += 25

            # Content with wrapping (limit to fit screen)
            max_chars_per_line = 25
            if len(content) > max_chars_per_line:
                draw.text((10, y_pos), content[:max_chars_per_line], font=fonts['medium'], fill=0)
                y_pos += 22
                if len(content) > max_chars_per_line * 2:
                    draw.text((10, y_pos), content[max_chars_per_line:max_chars_per_line*2], font=fonts['medium'], fill=0)
                    y_pos += 22
                    draw.text((10, y_pos), f"...({len(poem_api.full_content or 0)} chars total)", font=fonts['small'], fill=0)
                else:
                    draw.text((10, y_pos), content[max_chars_per_line:], font=fonts['medium'], fill=0)
            else:
                draw.text((10, y_pos), content, font=fonts['medium'], fill=0)
            y_pos += 30
        else:
            draw.text((10, y_pos), "Poetry data unavailable", font=fonts['medium'], fill=0)
            y_pos += 30

        # === System Info ===
        system_y = height - 60
        draw.line([(10, system_y), (width - 10, system_y)], fill=0, width=1)
        system_y += 10

        try:
            # Get IP address
            ip_address = get_ipaddress.get_ip_address()
            draw.text((10, system_y), f"IP: {ip_address}", font=fonts['small'], fill=0)
        except:
            draw.text((10, system_y), "IP: Not available", font=fonts['small'], fill=0)

        # Timestamp
        timestamp = datetime.now().strftime("%m-%d %H:%M")
        draw.text((width - 70, system_y), timestamp, font=fonts['small'], fill=0)

        logger.info("✅ Display image created successfully")
        return image

    except Exception as e:
        logger.error(f"❌ Failed to create display image: {e}")
        return None

def run_real_display_test():
    """Run the complete real e-paper display test"""
    global epd

    logger.info("🚀 Starting Real E-Paper Display Test")
    logger.info("=" * 50)

    # === Step 1: Test Hardware ===
    epd = test_hardware_initialization()
    if not epd:
        logger.error("❌ Cannot proceed without hardware initialization")
        return False

    # === Step 2: Load Dependencies ===
    get_config, get_weather, class_poem_api = load_dependencies()
    if not get_config:
        logger.error("❌ Cannot proceed without dependencies")
        return False

    # === Step 3: Load Fonts ===
    fonts = get_fonts()
    if not fonts:
        logger.error("❌ Cannot proceed without fonts")
        return False

    # === Step 4: Fetch Data ===
    weather_data, poem_data = fetch_display_data(get_config, get_weather, class_poem_api)

    # === Step 5: Create and Display Image ===
    display_image = create_display_image(weather_data, poem_data, fonts, epd)
    if not display_image:
        logger.error("❌ Cannot create display image")
        return False

    try:
        # Display on real hardware
        logger.info("🖥️ Displaying on e-paper hardware...")
        epd.display(epd.getbuffer(display_image))
        epd.refresh()

        logger.info("✅ Image displayed successfully on e-paper!")
        logger.info("👁️ Check your e-paper screen - it should show the weather and poetry data")

        # Keep the display active for viewing
        logger.info("⏱️ Display will remain active for 30 seconds...")
        time.sleep(30)

        logger.info("✅ Real e-paper display test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Display on hardware failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Real E-Paper Display Test")
    print("=" * 50)
    print("📋 This will test your connected e-paper hardware")
    print("⚠️  Make sure your e-paper display is properly connected")
    print("🔧 Press Ctrl+C to safely stop at any time")
    print("=" * 50)

    try:
        success = run_real_display_test()

        print("=" * 50)
        if success:
            print("✅ Real e-paper test completed!")
            print("🎯 Your hardware is working correctly!")
            print("📊 Check real_display_test.log for details")
        else:
            print("❌ Real e-paper test failed!")
            print("🔧 Check real_display_test.log for troubleshooting")

        # Cleanup
        cleanup_and_exit()

    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        cleanup_and_exit()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        cleanup_and_exit()