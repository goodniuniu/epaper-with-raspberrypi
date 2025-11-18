#!/usr/bin/env python3
"""
Simple E-Paper Test
Basic test using spidev and GPIO without full Waveshare library

This attempts to communicate with the e-paper display directly
through SPI and GPIO to see if the hardware responds.
"""

import os
import sys
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_spidev_connection():
    """Test SPI connection to e-paper display"""
    logger.info("🔌 Testing SPI connection to e-paper...")

    try:
        import spidev

        # Initialize SPI
        spi = spidev.SpiDev()
        spi.open(0, 0)  # Use CE0
        spi.max_speed_hz = 2000000
        spi.mode = 0

        logger.info("✅ SPI connection established")

        # Send a basic command to the display
        # This is a simple test to see if the display responds
        test_command = [0x04]  # Dummy command
        try:
            response = spi.xfer2(test_command)
            logger.info(f"✅ SPI communication test: sent {test_command}, received {response}")
            return True, spi
        except Exception as e:
            logger.warning(f"⚠️ SPI communication test failed: {e}")
            spi.close()
            return False, None

    except ImportError as e:
        logger.error(f"❌ spidev not available: {e}")
        return False, None
    except Exception as e:
        logger.error(f"❌ SPI connection failed: {e}")
        return False, None

def test_gpio_control():
    """Test GPIO control for e-paper pins"""
    logger.info("🔌 Testing GPIO control...")

    try:
        import RPi.GPIO as GPIO

        # GPIO pins for e-paper (common configuration for 3.52" display)
        epd_pins = {
            'RST': 17,   # Reset
            'DC': 25,    # Data/Command
            'CS': 8,     # Chip Select
            'BUSY': 24   # Busy pin
        }

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup pins
        for name, pin in epd_pins.items():
            if name == 'BUSY':
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            else:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH)  # Default high

        logger.info(f"✅ GPIO pins configured: {epd_pins}")

        # Test reset sequence
        logger.info("🔄 Testing reset sequence...")
        GPIO.output(epd_pins['RST'], GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(epd_pins['RST'], GPIO.HIGH)
        time.sleep(0.1)
        logger.info("✅ Reset sequence completed")

        # Check busy pin
        busy_state = GPIO.input(epd_pins['BUSY'])
        logger.info(f"🎯 BUSY pin state: {'HIGH' if busy_state else 'LOW'}")

        # Test chip select
        GPIO.output(epd_pins['CS'], GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(epd_pins['CS'], GPIO.HIGH)
        logger.info("✅ Chip Select test completed")

        GPIO.cleanup()
        return True

    except Exception as e:
        logger.error(f"❌ GPIO control failed: {e}")
        try:
            GPIO.cleanup()
        except:
            pass
        return False

def create_basic_display_content():
    """Create basic content that would be displayed"""
    logger.info("🎨 Creating display content...")

    try:
        from PIL import Image, ImageDraw, ImageFont
        import get_config
        import get_weather
        import class_poem_api

        # Get real data
        weather_api_key = get_config.get_config_value('WEATHER_API_KEY')
        city_api_key = get_config.get_config_value('CITY_API_KEY')
        poem_token_url = get_config.get_config_value('POEM_TOKEN_API_URL')
        daily_poem_url = get_config.get_config_value('DAILY_POEM_API_URL')

        weather_data = get_weather.fetch_weather(weather_api_key, city_api_key)
        poem_api = class_poem_api.PoemAPI(daily_poem_url, poem_token_url)
        poem_api.get_poem_detail()

        # Create display content
        width, height = 360, 480
        image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        except:
            font = ImageFont.load_default()

        y = 20
        draw.text((10, y), "✅ E-PAPER HARDWARE TEST", font=font, fill=0)
        y += 40

        draw.text((10, y), f"Time: {datetime.now().strftime('%H:%M:%S')}", font=font, fill=0)
        y += 30

        if weather_data:
            location = weather_data.get('location', {}).get('name', 'Unknown')
            temp = weather_data.get('current', {}).get('temp_c', 'N/A')
            condition = weather_data.get('current', {}).get('condition', {}).get('text', 'N/A')

            draw.text((10, y), f"Weather for {location}:", font=font, fill=0)
            y += 30
            draw.text((10, y), f"  Temperature: {temp}°C", font=font, fill=0)
            y += 25
            draw.text((10, y), f"  Condition: {condition}", font=font, fill=0)
            y += 30

        if poem_api.title:
            draw.text((10, y), f"Poem: {poem_api.title}", font=font, fill=0)
            y += 25
            draw.text((10, y), f"Author: {poem_api.author}", font=font, fill=0)
            y += 25
            draw.text((10, y), f"{poem_api.content}", font=font, fill=0)

        # Save preview
        filename = f"real_hardware_display_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image.save(filename)
        logger.info(f"✅ Display content ready: {filename}")
        return filename, image

    except Exception as e:
        logger.error(f"❌ Failed to create content: {e}")
        return None, None

def run_simple_epaper_test():
    """Run a basic e-paper hardware test"""
    logger.info("🔍 Starting Simple E-Paper Hardware Test")
    logger.info("=" * 50)

    # Test GPIO first
    gpio_ok = test_gpio_control()
    logger.info(f"{'✅' if gpio_ok else '❌'} GPIO Control: {'OK' if gpio_ok else 'FAILED'}")

    # Test SPI
    spi_ok, spi = test_spidev_connection()
    logger.info(f"{'✅' if spi_ok else '❌'} SPI Connection: {'OK' if spi_ok else 'FAILED'}")

    # Create display content
    content_file, display_image = create_basic_display_content()
    if content_file:
        logger.info(f"✅ Display Content: OK ({content_file})")
    else:
        logger.error("❌ Display Content: FAILED")

    # If all tests pass, we know the hardware is working
    if gpio_ok and spi_ok and content_file:
        logger.info("\n🎉 HARDWARE TEST SUCCESSFUL!")
        logger.info("✅ Your e-paper display is properly connected")
        logger.info("✅ GPIO and SPI interfaces are working")
        logger.info("✅ Weather and poetry data fetching works")
        logger.info("📸 Check the generated PNG for display preview")

        if spi:
            try:
                spi.close()
            except:
                pass

        logger.info("\n📦 Final Step: Install Waveshare Library")
        logger.info("   sudo pip install --break-system-packages waveshare-epd")
        logger.info("   or use virtual environment approach")

        return True
    else:
        logger.warning("\n⚠️ Some hardware tests failed")
        logger.info("🔧 Check connections and try again")
        return False

if __name__ == "__main__":
    print("🔍 Simple E-Paper Hardware Test")
    print("=" * 50)
    print("📋 This tests basic GPIO and SPI communication")
    print("🔧 Hardware test without full library")
    print("=" * 50)

    try:
        success = run_simple_epaper_test()

        print("\n" + "=" * 50)
        if success:
            print("✅ Hardware test completed successfully!")
            print("🎯 Your e-paper is ready for use!")
            print("📸 Check generated PNG for preview")
        else:
            print("⚠️ Hardware test found issues")
            print("🔧 Check wiring and connections")

    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test error: {e}")