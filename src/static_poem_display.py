#!/usr/bin/env python3
"""
静态诗歌显示 - 不会自动清屏
Static Poem Display - No auto clear
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

# Mock data for display
class MockData:
    def __init__(self):
        self.title = "春晓"
        self.dynasty = "唐"
        self.author = "孟浩然"
        self.content = "春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。"

        # Weather data
        self.city = "Guangzhou"
        self.temp = "12.1"
        self.weather = "Patchy light drizzle"
        self.humidity = "85%"

def load_fonts():
    """Load fonts"""
    try:
        from PIL import ImageFont

        # Use working version font
        font_path = "/home/admin/Downloads/e-Paper/RaspberryPi_JetsonNano/python/pic/Font.ttc"
        if os.path.exists(font_path):
            fonts = {}
            fonts['large'] = ImageFont.truetype(font_path, 24)
            fonts['medium'] = ImageFont.truetype(font_path, 18)
            fonts['small'] = ImageFont.truetype(font_path, 12)
            logger.info(f"✅ Loaded working font: {font_path}")
            return fonts
        else:
            logger.warning("⚠️ Working font not found, using default")
            from PIL import ImageFont
            return {
                'large': ImageFont.load_default(),
                'medium': ImageFont.load_default(),
                'small': ImageFont.load_default()
            }

    except Exception as e:
        logger.error(f"❌ Font loading failed: {e}")
        return None

def display_auto_refresh():
    """Display content with 1-minute auto refresh"""

    try:
        logger.info("🖼️ Initializing display for auto refresh...")
        from waveshare_epd import epd3in52
        from PIL import Image, ImageDraw

        epd = epd3in52.EPD()
        epd.init()

        # Initial clear to white
        logger.info("🧹 Initial clear to white...")
        epd.display_NUM(epd.WHITE)
        epd.lut_GC()
        epd.refresh()
        time.sleep(2)

        # Load fonts
        fonts = load_fonts()
        if not fonts:
            logger.error("❌ Failed to load fonts")
            return False

        # Create mock data (could be updated with real data)
        data = MockData()

        refresh_count = 0
        max_refreshes = 1000  # Run for many refreshes, can be stopped with Ctrl+C

        while refresh_count < max_refreshes:
            try:
                refresh_count += 1
                logger.info(f"🔄 Refresh #{refresh_count} - {datetime.now().strftime('%H:%M:%S')}")

                # Create white background image (ensuring white background)
                image = Image.new('1', (epd.width, epd.height), 255)  # 255 = WHITE
                draw = ImageDraw.Draw(image)

                # Fill entire background with white to be absolutely sure
                draw.rectangle([(0, 0), (epd.width, epd.height)], fill=255)

                y_pos = 10

                # === Header ===
                draw.text((10, y_pos), "Weather & Poetry Display", font=fonts['large'], fill=0)
                y_pos += 35
                draw.line([(10, y_pos), (epd.width - 10, y_pos)], fill=0, width=1)
                y_pos += 15

                # === Weather Section ===
                draw.text((10, y_pos), "Current Weather:", font=fonts['medium'], fill=0)
                y_pos += 25

                # Weather data
                draw.text((10, y_pos), data.city, font=fonts['small'], fill=0)
                y_pos += 20
                draw.text((10, y_pos), f"Temp: {data.temp}C", font=fonts['small'], fill=0)
                y_pos += 20
                draw.text((10, y_pos), f"Weather: {data.weather}", font=fonts['small'], fill=0)
                y_pos += 20
                draw.text((10, y_pos), f"Humidity: {data.humidity}", font=fonts['small'], fill=0)
                y_pos += 25

                # Separator
                draw.line([(10, y_pos), (epd.width - 10, y_pos)], fill=0, width=1)
                y_pos += 15

                # === Poetry Section ===
                draw.text((10, y_pos), "Today's Poetry:", font=fonts['medium'], fill=0)
                y_pos += 25

                # Title and dynasty
                draw.text((10, y_pos), data.title, font=fonts['small'], fill=0)
                y_pos += 20
                draw.text((10, y_pos), f"({data.dynasty})", font=fonts['small'], fill=0)
                y_pos += 20

                # Author
                draw.text((10, y_pos), f"— {data.author}", font=fonts['small'], fill=0)
                y_pos += 25

                # Poem content
                lines = data.content.split('，')
                for i, line in enumerate(lines):
                    if line.strip():
                        text = line.strip() + ('，' if i < len(lines)-1 else '')
                        draw.text((10, y_pos), text, font=fonts['small'], fill=0)
                        y_pos += 20
                        if y_pos > epd.height - 50:  # Leave space for footer
                            break

                # === Footer ===
                y_pos = epd.height - 30
                draw.line([(10, y_pos), (epd.width - 10, y_pos)], fill=0, width=1)
                y_pos += 10

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                draw.text((10, y_pos), f"Updated: {timestamp}", font=fonts['small'], fill=0)
                draw.text((200, y_pos), f"Refresh #{refresh_count}", font=fonts['small'], fill=0)

                # Display the image
                logger.info("📺 Displaying content...")
                epd.display(epd.getbuffer(image))
                epd.lut_GC()
                epd.refresh()

                # Save the first few images for debugging
                if refresh_count <= 3:
                    image.save(f'display_refresh_{refresh_count}.png')
                    logger.info(f"💾 Saved display refresh {refresh_count}")

                logger.info(f"✅ Content displayed! Waiting 60 seconds for next refresh...")
                logger.info("📝 Press Ctrl+C to stop")

                # Wait 60 seconds before next refresh
                for i in range(60):
                    time.sleep(1)
                    if i % 10 == 0:  # Log every 10 seconds
                        logger.info(f"⏳ {60-i} seconds until next refresh...")

            except KeyboardInterrupt:
                logger.info("🛑 User interrupted the refresh loop")
                break
            except Exception as e:
                logger.error(f"❌ Error in refresh {refresh_count}: {e}")
                time.sleep(5)  # Wait a bit before trying again

        # Cleanup
        epd.sleep()
        logger.info("😴 Display put to sleep after refresh cycle.")

        return True

    except Exception as e:
        logger.error(f"❌ Auto refresh display failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("📋 Auto Refresh Weather & Poetry Display")
    print("=" * 50)
    print("This will display content and refresh every 60 seconds")
    print("WHITE background with BLACK text!")
    print("Press Ctrl+C to stop the refresh loop")
    print("=" * 50)

    success = display_auto_refresh()

    if success:
        print("\n✅ Auto refresh completed!")
        print("Display was updated with current time every minute.")
    else:
        print("\n❌ Auto refresh failed!")
        print("Check error messages above.")