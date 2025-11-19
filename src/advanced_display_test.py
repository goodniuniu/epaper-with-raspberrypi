#!/usr/bin/env python3
"""
Advanced E-paper Display Test
This will test the display with multiple patterns and debug information
"""

import sys
import os
import time
import logging

# Add e-paper library path
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('advanced_display_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_display_patterns():
    """Test various display patterns to verify e-paper functionality"""

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

        # Wait for clear to complete
        time.sleep(3)

        # Test 2: Simple pattern
        logger.info("🎨 Test 2: Creating simple test pattern...")
        image = Image.new('1', (width, height), 255)  # White background
        draw = ImageDraw.Draw(image)

        # Draw test pattern
        draw.rectangle([10, 10, width-10, height-10], outline=0, width=2)
        draw.text((20, 30), "E-PAPER TEST", fill=0)
        draw.text((20, 60), f"Size: {width}x{height}", fill=0)
        draw.line([(20, 90), (width-20, 90)], fill=0, width=1)
        draw.text((20, 100), "如果你能看到这个", fill=0)
        draw.text((20, 120), "说明电子墨水屏工作正常!", fill=0)

        # Display pattern
        logger.info("📺 Displaying test pattern...")
        epd.display(epd.getbuffer(image))
        logger.info("✅ Test pattern displayed")

        # Wait for display to update
        time.sleep(5)

        # Test 3: Full black and white
        logger.info("⚫ Test 3: Full black screen...")
        black_image = Image.new('1', (width, height), 0)  # Black background
        epd.display(epd.getbuffer(black_image))
        logger.info("✅ Black screen displayed")

        time.sleep(3)

        logger.info("⚪ Test 4: Full white screen...")
        white_image = Image.new('1', (width, height), 255)  # White background
        epd.display(epd.getbuffer(white_image))
        logger.info("✅ White screen displayed")

        time.sleep(3)

        # Test 5: Weather display simulation
        logger.info("🌤️ Test 5: Weather display simulation...")
        weather_image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(weather_image)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 18)
        except:
            font = ImageFont.load_default()

        # Weather info
        draw.text((10, 10), "Weather Display Test", font=font, fill=0)
        draw.text((10, 40), "📍 Beijing", font=font, fill=0)
        draw.text((10, 70), "🌡️ 15.0°C", font=font, fill=0)
        draw.text((10, 100), "☁️ Cloudy", font=font, fill=0)
        draw.text((10, 130), "💧 65% humidity", font=font, fill=0)

        # Add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((10, height-30), f"Updated: {timestamp}", font=font, fill=0)

        epd.display(epd.getbuffer(weather_image))
        logger.info("✅ Weather simulation displayed")

        # Save test images
        image.save('test_pattern.png')
        weather_image.save('weather_simulation.png')
        logger.info("💾 Test images saved")

        # Final wait
        time.sleep(5)

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

def check_hardware_connections():
    """Check common hardware connection issues"""

    logger.info("🔍 Checking hardware connections...")

    checks = [
        ("SPI", "/dev/spidev0.0"),
        ("I2C", "/dev/i2c-1"),
        ("GPIO", "/sys/class/gpio"),
    ]

    for name, path in checks:
        if os.path.exists(path):
            logger.info(f"✅ {name} interface available: {path}")
        else:
            logger.warning(f"⚠️ {name} interface not found: {path}")

    # Check for BCM2835
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'BCM2835' in cpuinfo or 'BCM2711' in cpuinfo:
                logger.info("✅ Raspberry Pi detected")
            else:
                logger.warning("⚠️ Not a standard Raspberry Pi")
    except:
        logger.warning("⚠️ Could not detect Raspberry Pi")

if __name__ == "__main__":
    print("🧪 Advanced E-paper Display Test")
    print("=" * 50)
    print("This will test your e-paper display with multiple patterns")
    print("Watch the screen carefully and report what you see")
    print("=" * 50)

    # Check hardware first
    check_hardware_connections()

    # Run display tests
    success = test_display_patterns()

    if success:
        print("\n✅ Advanced display test completed successfully!")
        print("If you didn't see any changes on your e-paper screen:")
        print("1. Check physical connections (SPI, VCC, GND, etc.)")
        print("2. Verify power supply is adequate")
        print("3. Check if the display model is correct")
        print("4. Look at the log file for detailed errors")
    else:
        print("\n❌ Advanced display test failed!")
        print("Check the log file 'advanced_display_test.log' for details")

    print("👋 Test complete!")