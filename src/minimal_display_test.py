#!/usr/bin/env python3
"""
Minimal E-paper Display Test
Just basic patterns to verify display functionality
"""

import sys
import os
import time

# Add e-paper library path
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

def minimal_test():
    """Minimal test with basic patterns"""

    try:
        print("🔧 Importing e-paper library...")
        import waveshare_epd.epd3in52 as epd3in52
        from PIL import Image, ImageDraw

        print("✅ Library imported successfully")

        print("🖼️ Creating EPD driver...")
        epd = epd3in52.EPD()

        print("⚡ Initializing hardware...")
        epd.init()
        print("✅ Hardware initialized")

        width, height = epd.width, epd.height
        print(f"📐 Display size: {width}x{height}")

        # Test 1: Completely black screen
        print("⚫ Test 1: Black screen...")
        black_image = Image.new('1', (width, height), 0)  # All black
        epd.display(epd.getbuffer(black_image))
        print("✅ Black screen displayed")
        time.sleep(5)

        # Test 2: Completely white screen
        print("⚪ Test 2: White screen...")
        white_image = Image.new('1', (width, height), 255)  # All white
        epd.display(epd.getbuffer(white_image))
        print("✅ White screen displayed")
        time.sleep(5)

        # Test 3: Half black, half white
        print("⚫⚪ Test 3: Half and half...")
        half_image = Image.new('1', (width, height), 255)  # White background
        draw = ImageDraw.Draw(half_image)
        draw.rectangle([0, 0, width//2, height], fill=0)  # Left half black
        epd.display(epd.getbuffer(half_image))
        print("✅ Half screen displayed")
        time.sleep(5)

        # Test 4: Simple text with default font
        print("📝 Test 4: Simple text...")
        text_image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(text_image)

        # Use default font
        from PIL import ImageFont
        font = ImageFont.load_default()

        # Add simple text
        draw.text((10, 10), "HELLO", font=font, fill=0)
        draw.text((10, 30), "WORLD", font=font, fill=0)
        draw.text((10, 50), "12345", font=font, fill=0)

        epd.display(epd.getbuffer(text_image))
        print("✅ Text displayed")
        time.sleep(5)

        # Cleanup
        print("😴 Putting display to sleep...")
        epd.sleep()
        print("✅ Test completed successfully!")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Minimal E-paper Display Test")
    print("=" * 40)
    print("This will show basic patterns")
    print("Watch what appears on your screen:")
    print("1. All black screen")
    print("2. All white screen")
    print("3. Half black/white screen")
    print("4. Simple English text")
    print("=" * 40)
    print()

    success = minimal_test()

    if success:
        print("\n✅ Minimal test completed!")
        print("If you saw the different patterns, your display is working!")
        print("If you only saw stripes, there might be a connection issue.")
    else:
        print("\n❌ Test failed - check error messages above")