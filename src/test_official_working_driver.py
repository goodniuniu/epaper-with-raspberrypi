#!/usr/bin/env python3
"""
基于官方工作版本的测试脚本
Based on the official working version from examples/epd_3in52_test.py
"""

import sys
import os
import time
import logging
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use the exact same path setup as the working version
current_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(os.path.dirname(current_dir), 'lib')
picdir = os.path.join(os.path.dirname(current_dir), 'pic')

logger.info(f"📁 Current directory: {current_dir}")
logger.info(f"📁 Library directory: {libdir}")
logger.info(f"📁 Picture directory: {picdir}")

if os.path.exists(libdir):
    sys.path.append(libdir)
    logger.info(f"✅ Added {libdir} to Python path")
else:
    logger.warning(f"⚠️ Library directory {libdir} not found")
    # Fallback to the path used in current version
    fallback_libdir = os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib")
    if os.path.exists(fallback_libdir):
        sys.path.append(fallback_libdir)
        logger.info(f"✅ Using fallback library path: {fallback_libdir}")
    else:
        logger.error(f"❌ Neither library path found!")

try:
    # Use the exact same import as the working version
    from waveshare_epd import epd3in52
    logger.info("✅ Successfully imported epd3in52 from waveshare_epd")
except ImportError as e:
    logger.error(f"❌ Failed to import epd3in52: {e}")
    sys.exit(1)

def test_official_working_method():
    """Test using the exact same method as the official working version"""

    print("🚀 Official Working Method Test")
    print("=" * 50)
    print("This uses the exact same method as epd_3in52_test.py")
    print("which is the confirmed working version!")
    print("=" * 50)

    try:
        logger.info("🖼️ Initializing EPD using official working method...")
        epd = epd3in52.EPD()

        # Use the exact same initialization sequence as the working version
        logger.info("⚡ Step 1: Initialize hardware...")
        epd.init()

        logger.info("🧹 Step 2: Clear using display_NUM(WHITE)...")
        epd.display_NUM(epd.WHITE)  # This is the key difference!

        logger.info("🎨 Step 3: Load lookup table...")
        epd.lut_GC()

        logger.info("🔄 Step 4: Refresh display...")
        epd.refresh()

        logger.info("⏱️ Waiting for display to settle...")
        time.sleep(2)

        # Additional initialization from working version
        logger.info("🔧 Step 5: Send display configuration commands...")
        epd.send_command(0x50)
        epd.send_data(0x17)
        time.sleep(2)

        width, height = epd.width, epd.height
        logger.info(f"📐 Display size: {width}x{height}")

        # Test 1: Simple horizontal image (like in working version)
        logger.info("📝 Test 1: Drawing horizontal image...")
        Himage = Image.new('1', (epd.height, epd.width), 255)  # Note: height, width swapped!
        draw = ImageDraw.Draw(Himage)

        # Try to load the font from the working version
        font = None
        font_paths = [
            os.path.join(picdir, 'Font.ttc'),
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, 24)
                    logger.info(f"✅ Loaded font: {font_path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load font {font_path}: {e}")

        if font is None:
            font = ImageFont.load_default()
            logger.warning("⚠️ Using default font")

        # Draw simple test content
        draw.text((10, 0), 'hello world', font=font, fill=0)
        draw.text((10, 30), '3.52inch e-Paper Test', font=font, fill=0)
        draw.text((10, 60), 'Working Driver Version', font=font, fill=0)

        # Draw some shapes like in the working version
        draw.line((20, 100, 70, 150), fill=0)
        draw.line((70, 100, 20, 150), fill=0)
        draw.rectangle((20, 100, 70, 150), outline=0)
        draw.rectangle((100, 100, 150, 150), fill=0)

        logger.info("📺 Displaying horizontal image...")
        epd.display(epd.getbuffer(Himage))
        epd.lut_GC()  # Important: load LUT after display
        epd.refresh()
        time.sleep(3)

        # Save the test image
        Himage.save('official_working_test_horizontal.png')
        logger.info("💾 Saved horizontal test image")

        # Test 2: Vertical image (like in working version)
        logger.info("📝 Test 2: Drawing vertical image...")
        Limage = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(Limage)

        draw.text((2, 0), 'hello world', font=font, fill=0)
        draw.text((2, 30), 'Vertical Test', font=font, fill=0)
        draw.text((2, 60), 'If you see this', font=font, fill=0)
        draw.text((2, 90), 'It means the driver', font=font, fill=0)
        draw.text((2, 120), 'is working!', font=font, fill=0)

        logger.info("📺 Displaying vertical image...")
        epd.display(epd.getbuffer(Limage))
        epd.lut_GC()
        epd.refresh()
        time.sleep(3)

        # Save the vertical test image
        Limage.save('official_working_test_vertical.png')
        logger.info("💾 Saved vertical test image")

        # Test 3: Clear screen using the working method
        logger.info("🧹 Test 3: Clear screen using working method...")
        epd.Clear()
        time.sleep(2)

        logger.info("😴 Putting display to sleep...")
        epd.sleep()

        # Cleanup using the working method
        logger.info("🧹 Cleaning up GPIO...")
        epd3in52.epdconfig.module_exit(cleanup=True)

        logger.info("✅ Official working method test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Official working method test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_official_working_method()

    if success:
        print("\n✅ SUCCESS! The official working method works!")
        print("If you could see clear text and patterns, the issue was the driver method.")
        print("The key differences are:")
        print("- Using display_NUM(WHITE) instead of Clear()")
        print("- Using lut_GC() after display")
        print("- Using manual refresh()")
        print("- Different import and path setup")
    else:
        print("\n❌ Test failed! Check error messages above.")
        print("This means there might be a hardware connection issue.")