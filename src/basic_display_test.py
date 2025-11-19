#!/usr/bin/env python3
"""
Basic E-paper Display Test with English text only
Tests hardware functionality without character encoding issues
"""

import sys
import os
import time
import logging

# Add e-paper library path
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_display():
    """Test basic e-paper display with simple English text and patterns"""

    try:
        logger.info("🔧 Importing e-paper library...")
        import waveshare_epd.epd3in52 as epd3in52
        from PIL import Image, ImageDraw, ImageFont

        logger.info("✅ Library imported successfully")

        logger.info("🖼️ Creating EPD driver object...")
        epd = epd3in52.EPD()

        logger.info("⚡ Initializing hardware...")
        epd.init()
        logger.info("✅ Hardware initialized")

        width, height = epd.width, epd.height
        logger.info(f"📐 Display dimensions: {width}x{height}")

        # Test 1: Clear display
        logger.info("🧹 Test 1: Clearing display...")
        epd.Clear()
        logger.info("✅ Display cleared")
        time.sleep(3)

        # Test 2: Simple pattern with English text only
        logger.info("🎨 Test 2: Creating test pattern...")
        image = Image.new('1', (width, height), 255)  # White background
        draw = ImageDraw.Draw(image)

        # Use default font to avoid encoding issues
        font = ImageFont.load_default()

        # Draw test pattern
        draw.rectangle([10, 10, width-10, height-10], outline=0, width=2)
        draw.text((20, 30), "E-PAPER DISPLAY TEST", font=font, fill=0)
        draw.text((20, 50), f"Screen Size: {width}x{height}", font=font, fill=0)
        draw.text((20, 70), "If you can see this text", font=font, fill=0)
        draw.text((20, 90), "Your e-paper is working!", font=font, fill=0)
        draw.line([(20, 110), (width-20, 110)], fill=0, width=1)
        draw.text((20, 120), f"Test Time: {time.strftime('%H:%M:%S')}", font=font, fill=0)

        # Display pattern
        logger.info("📺 Displaying test pattern...")
        epd.display(epd.getbuffer(image))
        logger.info("✅ Test pattern displayed")
        image.save('basic_test_output.png')
        time.sleep(5)

        # Test 3: Black and white squares
        logger.info("⚫ Test 3: Black and white squares...")
        bw_image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(bw_image)

        # Draw checkerboard pattern
        square_size = 40
        for y in range(0, height, square_size * 2):
            for x in range(0, width, square_size * 2):
                draw.rectangle([x, y, x+square_size, y+square_size], fill=0)
                draw.rectangle([x+square_size, y+square_size, x+square_size*2, y+square_size*2], fill=0)

        epd.display(epd.getbuffer(bw_image))
        logger.info("✅ Checkerboard pattern displayed")
        bw_image.save('checkerboard_test.png')
        time.sleep(5)

        # Test 4: Weather simulation (English only)
        logger.info("🌤️ Test 4: Weather display simulation...")
        weather_image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(weather_image)

        draw.text((10, 10), "WEATHER DISPLAY", font=font, fill=0)
        draw.text((10, 40), "Location: Guangzhou", font=font, fill=0)
        draw.text((10, 60), "Temperature: 13.2C", font=font, fill=0)
        draw.text((10, 80), "Condition: Light rain", font=font, fill=0)
        draw.text((10, 100), "Humidity: 85%", font=font, fill=0)

        timestamp = time.strftime("%Y-%m-%d %H:%M")
        draw.text((10, height-30), f"Updated: {timestamp}", font=font, fill=0)

        epd.display(epd.getbuffer(weather_image))
        logger.info("✅ Weather simulation displayed")
        weather_image.save('weather_test_english.png')
        time.sleep(5)

        # Test 5: Full refresh clear
        logger.info("🧹 Test 5: Final clear...")
        epd.Clear()
        logger.info("✅ Final clear complete")

        # Cleanup
        logger.info("😴 Putting display to sleep...")
        epd.sleep()
        logger.info("✅ Display sleep complete")

        return True

    except Exception as e:
        logger.error(f"❌ Display test failed: {e}")
        import traceback
        logger.error(f"📋 Full error: {traceback.format_exc()}")
        return False

def check_gpio_pins():
    """Check if GPIO pins are accessible"""

    logger.info("🔍 Checking GPIO access...")
    try:
        import RPi.GPIO as GPIO
        logger.info("✅ RPi.GPIO library available")

        # Try to set mode
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        logger.info("✅ GPIO access confirmed")
        return True
    except Exception as e:
        logger.warning(f"⚠️ GPIO access issue: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Basic E-paper Display Test")
    print("=" * 50)
    print("This tests e-paper with English text only")
    print("Watch your e-paper screen carefully")
    print("=" * 50)
    print()

    # Check GPIO
    check_gpio_pins()

    # Run display tests
    success = test_basic_display()

    if success:
        print("\n✅ Basic display test completed successfully!")
        print("\n📊 Test Results:")
        print("- If you saw text and patterns: E-paper is working!")
        print("- If screen stayed blank: Check hardware connections")
        print("- If screen partially worked: Power or connection issue")
        print("\n🔧 Hardware Checks:")
        print("1. SPI connection: MOSI, MISO, SCLK, CS")
        print("2. Power: VCC (3.3V/5V), GND")
        print("3. Control: DC, RST, BUSY")
        print("4. Make sure ribbon cable is secure")
    else:
        print("\n❌ Basic display test failed!")
        print("Check the error messages above for troubleshooting")

    print("\n👋 Test complete!")