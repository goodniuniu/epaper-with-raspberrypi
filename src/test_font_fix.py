#!/usr/bin/env python3
"""
Font Fix Test Script
Test if the font fix resolves the gray screen issue
"""

import sys
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up Python path
current_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(os.path.dirname(current_dir), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
else:
    fallback_libdir = os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib")
    if os.path.exists(fallback_libdir):
        sys.path.append(fallback_libdir)

def test_simple_display():
    """Test simple display with minimal font usage"""

    try:
        logger.info("🖼️ Initializing display for font test...")
        from waveshare_epd import epd3in52
        from PIL import Image, ImageDraw, ImageFont

        epd = epd3in52.EPD()
        epd.init()
        epd.display_NUM(epd.WHITE)
        epd.lut_GC()
        epd.refresh()
        time.sleep(1)

        # Create simple test image
        logger.info("🎨 Creating test image...")
        image = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(image)

        # Test 1: Use default font first
        logger.info("📝 Testing with default font...")
        default_font = ImageFont.load_default()
        draw.text((10, 10), "Default Font Test", font=default_font, fill=0)
        draw.text((10, 30), "Weather: 25C", font=default_font, fill=0)
        draw.text((10, 50), "Status: OK", font=default_font, fill=0)

        logger.info("📺 Displaying with default font...")
        epd.display(epd.getbuffer(image))
        epd.lut_GC()
        epd.refresh()
        time.sleep(3)

        # Test 2: Try TrueType fonts one by one
        font_paths = [
            "/home/admin/Downloads/e-Paper/RaspberryPi_JetsonNano/python/pic/Font.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        for i, font_path in enumerate(font_paths):
            if os.path.exists(font_path):
                logger.info(f"🔍 Testing font {i+1}: {font_path}")

                try:
                    # Clear image
                    image = Image.new('1', (epd.width, epd.height), 255)
                    draw = ImageDraw.Draw(image)

                    # Load font
                    font = ImageFont.truetype(font_path, 18)

                    # Test with simple English text
                    draw.text((10, 10), f"Font Test {i+1}", font=font, fill=0)
                    draw.text((10, 35), f"Path: {os.path.basename(font_path)}", font=font, fill=0)
                    draw.text((10, 60), "Weather: 25C, Sunny", font=font, fill=0)
                    draw.text((10, 85), "Hello World Test", font=font, fill=0)

                    # Test with simple Chinese (if available)
                    draw.text((10, 120), "Chinese Test: 中文", font=font, fill=0)

                    logger.info(f"📺 Displaying with font {i+1}...")
                    epd.display(epd.getbuffer(image))
                    epd.lut_GC()
                    epd.refresh()
                    time.sleep(3)

                    logger.info(f"✅ Font {i+1} rendered successfully")

                except Exception as e:
                    logger.warning(f"❌ Font {i+1} failed: {e}")
                    continue
            else:
                logger.warning(f"⚠️ Font {i+1} not found: {font_path}")

        # Clear screen at the end
        logger.info("🧹 Clearing screen...")
        epd.Clear()
        epd.sleep()

        logger.info("✅ Font test completed!")
        return True

    except Exception as e:
        logger.error(f"❌ Font test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Font Fix Test")
    print("=" * 30)
    print("This will test different fonts to identify the gray screen issue")
    print("=" * 30)

    success = test_simple_display()

    if success:
        print("\n✅ Font test completed!")
        print("If you saw clear text with default font but gray with TrueType fonts,")
        print("the issue is font-related. We need to use the working font.")
    else:
        print("\n❌ Font test failed!")
        print("Check error messages above.")