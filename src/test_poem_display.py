#!/usr/bin/env python3
"""
测试诗歌显示功能
Test poem display functionality
"""

import sys
import os
import time
import logging
from datetime import datetime

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

# Mock poem data for testing
class MockPoemData:
    def __init__(self):
        self.title = "春晓"
        self.dynasty = "唐"
        self.author = "孟浩然"
        self.content = "春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。"

def load_fonts():
    """Load fonts"""
    fonts = {}

    try:
        from PIL import ImageFont

        # Use working version font
        font_path = "/home/admin/Downloads/e-Paper/RaspberryPi_JetsonNano/python/pic/Font.ttc"
        if os.path.exists(font_path):
            fonts['large'] = ImageFont.truetype(font_path, 24)
            fonts['medium'] = ImageFont.truetype(font_path, 18)
            fonts['small'] = ImageFont.truetype(font_path, 12)
            logger.info(f"✅ Loaded working font: {font_path}")
        else:
            fonts['large'] = fonts['medium'] = fonts['small'] = ImageFont.load_default()
            logger.warning("⚠️ Using default fonts")

    except Exception as e:
        logger.error(f"❌ Font loading failed: {e}")
        return None

    return fonts

def test_poem_display():
    """Test poem display with mock data"""

    try:
        logger.info("🖼️ Initializing display for poem test...")
        from waveshare_epd import epd3in52
        from PIL import Image, ImageDraw

        epd = epd3in52.EPD()
        epd.init()
        epd.display_NUM(epd.WHITE)
        epd.lut_GC()
        epd.refresh()
        time.sleep(1)

        # Load fonts
        fonts = load_fonts()
        if not fonts:
            logger.error("❌ Failed to load fonts")
            return False

        # Create mock poem data
        poem_data = MockPoemData()
        logger.info(f"📜 Using mock poem: {poem_data.title} by {poem_data.author}")

        # Create test image - White background with black text
        logger.info("🎨 Creating poem display image (white background)...")
        image = Image.new('1', (epd.width, epd.height), 255)  # 255 = white background
        draw = ImageDraw.Draw(image)

        y_pos = 10

        # === Header ===
        draw.text((10, y_pos), "Weather & Poetry Display", font=fonts['large'], fill=0)
        y_pos += 35
        draw.line([(10, y_pos), (epd.width - 10, y_pos)], fill=0, width=1)
        y_pos += 15

        # === Weather Section ===
        draw.text((10, y_pos), "Current Weather:", font=fonts['medium'], fill=0)
        y_pos += 25

        # Mock weather data
        draw.text((10, y_pos), "Guangzhou", font=fonts['small'], fill=0)
        y_pos += 20
        draw.text((10, y_pos), "Temp: 12.1C", font=fonts['small'], fill=0)
        y_pos += 20
        draw.text((10, y_pos), "Weather: Patchy light drizzle", font=fonts['small'], fill=0)
        y_pos += 20
        draw.text((10, y_pos), "Humidity: 85%", font=fonts['small'], fill=0)
        y_pos += 20

        y_pos += 10
        draw.line([(10, y_pos), (epd.width - 10, y_pos)], fill=0, width=1)
        y_pos += 15

        # === Poetry Section ===
        draw.text((10, y_pos), "Today's Poetry:", font=fonts['medium'], fill=0)
        y_pos += 25

        # Title and dynasty
        try:
            draw.text((10, y_pos), poem_data.title, font=fonts['small'], fill=0)
            y_pos += 20
            draw.text((10, y_pos), f"({poem_data.dynasty})", font=fonts['small'], fill=0)
            y_pos += 20
        except Exception as e:
            logger.warning(f"Could not render title: {e}")
            draw.text((10, y_pos), "Poem Title", font=fonts['small'], fill=0)
            y_pos += 40

        # Author
        author_text = f"— {poem_data.author}"
        try:
            draw.text((10, y_pos), author_text, font=fonts['small'], fill=0)
            y_pos += 20
        except Exception as e:
            logger.warning(f"Could not render author: {e}")
            draw.text((10, y_pos), "Unknown Author", font=fonts['small'], fill=0)
            y_pos += 20

        # Poem content
        if poem_data.content:
            y_pos += 5
            try:
                logger.info(f"🎨 Rendering poem content: '{poem_data.content}'")
                # Split content and show first few lines
                lines = poem_data.content.split('，')
                for i, line in enumerate(lines[:4]):  # Show max 4 lines
                    if line.strip():
                        text_to_render = line.strip() + ('，' if i < len(lines)-1 else '')
                        logger.info(f"🎨 Rendering line {i+1}: '{text_to_render}'")
                        draw.text((10, y_pos), text_to_render, font=fonts['small'], fill=0)
                        y_pos += 20
                        if y_pos > epd.height - 80:  # Prevent overflow
                            break
            except Exception as e:
                logger.warning(f"Could not render poem content: {e}")
                draw.text((10, y_pos), "Poem content error", font=fonts['small'], fill=0)

        # === Footer ===
        y_pos = epd.height - 30
        draw.line([(10, y_pos), (epd.width - 10, y_pos)], fill=0, width=1)
        y_pos += 10

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        draw.text((10, y_pos), f"Updated: {timestamp}", font=fonts['small'], fill=0)

        # Display the image
        logger.info("📺 Displaying poem test image...")
        epd.display(epd.getbuffer(image))
        epd.lut_GC()
        epd.refresh()

        # Save the image
        image.save('poem_test_display.png')
        logger.info("💾 Poem test image saved as 'poem_test_display.png'")

        time.sleep(10)

        # Put display to sleep but keep the content
        logger.info("😴 Putting display to sleep (keeping content)...")
        epd.sleep()

        logger.info("✅ Poem display test completed successfully!")
        logger.info("📝 Content will remain on screen until next refresh.")
        return True

    except Exception as e:
        logger.error(f"❌ Poem display test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Poem Display Test")
    print("=" * 30)
    print("This will test the complete weather + poetry display")
    print("using mock poem data since the API is failing.")
    print("=" * 30)

    success = test_poem_display()

    if success:
        print("\n✅ Poem display test completed!")
        print("You should now see a complete display with both weather and poetry.")
    else:
        print("\n❌ Poem display test failed!")
        print("Check error messages above.")