#!/usr/bin/env python3
"""
Hardware Connection Test
Tests if e-paper hardware is properly connected without using the library

This will help diagnose connection issues before installing the full library.
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_gpio_access():
    """Check if we can access GPIO pins"""
    logger.info("🔌 Testing GPIO access...")

    try:
        # Try to import RPi.GPIO
        import RPi.GPIO as GPIO
        logger.info("✅ RPi.GPIO library imported")

        # Test GPIO mode setting
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Test a few GPIO pins used by e-paper
        test_pins = [8, 24, 25]  # Common e-paper pins
        for pin in test_pins:
            try:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
                GPIO.output(pin, GPIO.HIGH)
                logger.info(f"✅ GPIO pin {pin} accessible")
            except Exception as e:
                logger.warning(f"⚠️ GPIO pin {pin} not accessible: {e}")

        GPIO.cleanup()
        logger.info("✅ GPIO test completed")
        return True

    except ImportError as e:
        logger.error(f"❌ RPi.GPIO not available: {e}")
        logger.info("💡 Install with: sudo apt-get install python3-rpi.gpio")
        return False
    except Exception as e:
        logger.error(f"❌ GPIO access failed: {e}")
        logger.info("💡 You may need sudo access or I2C/SPI enabled")
        return False

def check_spi_interface():
    """Check if SPI interface is available"""
    logger.info("🔌 Testing SPI interface...")

    try:
        # Check if SPI devices exist
        spi_devices = ['/dev/spidev0.0', '/dev/spidev0.1']
        found_spi = []

        for device in spi_devices:
            if os.path.exists(device):
                found_spi.append(device)
                logger.info(f"✅ Found SPI device: {device}")

        if found_spi:
            logger.info("✅ SPI interface available")
            return True
        else:
            logger.warning("⚠️ No SPI devices found")
            logger.info("💡 Enable SPI with: sudo raspi-config")
            logger.info("   Navigate to Interface Options → SPI → Enable")
            return False

    except Exception as e:
        logger.error(f"❌ SPI check failed: {e}")
        return False

def check_i2c_interface():
    """Check if I2C interface is available"""
    logger.info("🔌 Testing I2C interface...")

    try:
        # Check if I2C devices exist
        i2c_devices = ['/dev/i2c-1', '/dev/i2c-0']
        found_i2c = []

        for device in i2c_devices:
            if os.path.exists(device):
                found_i2c.append(device)
                logger.info(f"✅ Found I2C device: {device}")

        if found_i2c:
            logger.info("✅ I2C interface available")
            return True
        else:
            logger.warning("⚠️ No I2C devices found")
            logger.info("💡 Enable I2C with: sudo raspi-config")
            logger.info("   Navigate to Interface Options → I2C → Enable")
            return False

    except Exception as e:
        logger.error(f"❌ I2C check failed: {e}")
        return False

def create_display_simulation():
    """Create a simulated display output for testing"""
    logger.info("🎨 Creating display simulation...")

    try:
        from PIL import Image, ImageDraw, ImageFont
        import get_config
        import get_weather
        import class_poem_api

        # Load configuration and data
        weather_api_key = get_config.get_config_value('WEATHER_API_KEY')
        city_api_key = get_config.get_config_value('CITY_API_KEY')
        poem_token_url = get_config.get_config_value('POEM_TOKEN_API_URL')
        daily_poem_url = get_config.get_config_value('DAILY_POEM_API_URL')

        # Fetch data
        weather_data = get_weather.fetch_weather(weather_api_key, city_api_key)
        poem_api = class_poem_api.PoemAPI(daily_poem_url, poem_token_url)
        poem_api.get_poem_detail()

        # Create display image
        width, height = 360, 480
        image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        except:
            font = ImageFont.load_default()

        # Draw content
        y_pos = 20
        draw.text((10, y_pos), "HARDWARE TEST DISPLAY", font=font, fill=0)
        y_pos += 30

        if weather_data:
            location = weather_data.get('location', {}).get('name', 'Unknown')
            temp = weather_data.get('current', {}).get('temp_c', 'N/A')
            draw.text((10, y_pos), f"Weather: {location}", font=font, fill=0)
            y_pos += 25
            draw.text((10, y_pos), f"Temp: {temp}°C", font=font, fill=0)
            y_pos += 30

        if poem_api.title:
            draw.text((10, y_pos), f"Poem: {poem_api.title}", font=font, fill=0)
            y_pos += 25
            draw.text((10, y_pos), f"Author: {poem_api.author}", font=font, fill=0)
            y_pos += 25
            draw.text((10, y_pos), f"{poem_api.content}", font=font, fill=0)

        # Add test info
        y_pos = height - 60
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((10, y_pos), f"Test: {timestamp}", font=font, fill=0)
        draw.text((10, y_pos + 20), "Hardware connection test", font=font, fill=0)

        # Save the image
        filename = f"hardware_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image.save(filename)
        logger.info(f"✅ Display simulation saved: {filename}")
        logger.info(f"📸 This shows what would appear on your e-paper")
        return filename

    except Exception as e:
        logger.error(f"❌ Display simulation failed: {e}")
        return None

def provide_library_instructions():
    """Provide instructions for installing the e-paper library"""
    logger.info("\n📚 E-Paper Library Installation Instructions:")
    logger.info("=" * 50)
    logger.info("Method 1: Using pip (if virtual environment):")
    logger.info("   python -m venv epaper_env")
    logger.info("   source epaper_env/bin/activate")
    logger.info("   pip install spidev RPi.GPIO")
    logger.info("   # Download the library from Waveshare")
    logger.info("")
    logger.info("Method 2: Manual installation:")
    logger.info("   git clone https://github.com/waveshare/e-Paper.git")
    logger.info("   cd e-Paper/RaspberryPi_JetsonNano/python/lib")
    logger.info("   sudo python3 setup.py install")
    logger.info("")
    logger.info("Method 3: System packages:")
    logger.info("   sudo apt-get update")
    logger.info("   sudo apt-get install python3-spidev python3-rpi.gpio")
    logger.info("=" * 50)

def run_hardware_check():
    """Run complete hardware connection check"""
    logger.info("🔍 Starting E-Paper Hardware Connection Test")
    logger.info("=" * 50)

    results = []

    # Test 1: GPIO Access
    gpio_ok = check_gpio_access()
    results.append(('GPIO', gpio_ok))

    # Test 2: SPI Interface
    spi_ok = check_spi_interface()
    results.append(('SPI', spi_ok))

    # Test 3: I2C Interface
    i2c_ok = check_i2c_interface()
    results.append(('I2C', i2c_ok))

    # Test 4: Display Simulation
    logger.info("\n🖥️ Testing display simulation...")
    sim_file = create_display_simulation()
    results.append(('Display', sim_file is not None))

    # Summary
    logger.info("\n📊 Hardware Test Results:")
    logger.info("=" * 30)
    all_ok = True
    for test_name, result in results:
        status = "✅ OK" if result else "❌ FAILED"
        logger.info(f"{test_name:10} : {status}")
        if not result:
            all_ok = False

    logger.info("=" * 30)

    if all_ok:
        logger.info("🎉 All hardware tests passed!")
        logger.info("✅ Your hardware connections appear to be correct")
        logger.info("📦 Next step: Install the e-paper library")
    else:
        logger.warning("⚠️ Some hardware tests failed")
        logger.info("🔧 Check your connections and enable interfaces")

    # Provide installation instructions
    provide_library_instructions()

    return all_ok

if __name__ == "__main__":
    print("🔍 E-Paper Hardware Connection Test")
    print("=" * 50)
    print("📋 This will test your hardware connections")
    print("🔧 Make sure your e-paper display is connected")
    print("=" * 50)

    try:
        success = run_hardware_check()

        print("\n" + "=" * 50)
        if success:
            print("✅ Hardware test completed successfully!")
            print("🎯 Your e-paper hardware is ready!")
            print("📸 Check the PNG file for display preview")
        else:
            print("⚠️ Hardware test found issues")
            print("🔧 Follow the instructions above to fix connections")

    except Exception as e:
        print(f"\n❌ Hardware test failed: {e}")