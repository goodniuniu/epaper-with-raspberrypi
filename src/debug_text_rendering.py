#!/usr/bin/env python3
"""
Debug Text Rendering
诊断为什么文字没有显示出来
"""

import sys
import os
import time

# Add e-paper library path
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

def debug_text():
    """Debug text rendering step by step"""

    try:
        print("🔍 Debug Text Rendering")
        print("=" * 40)

        import waveshare_epd.epd3in52 as epd3in52
        from PIL import Image, ImageDraw

        print("✅ Libraries imported")

        epd = epd3in52.EPD()
        epd.init()

        width, height = epd.width, epd.height
        print(f"📐 Display size: {width}x{height}")

        # Test 1: Create image and verify it has content
        print("🎨 Test 1: Creating simple image...")
        test_image = Image.new('1', (width, height), 255)  # White background
        draw = ImageDraw.Draw(test_image)

        # Add a simple black rectangle to verify basic drawing works
        draw.rectangle([50, 50, 100, 100], fill=0)
        print("✅ Black rectangle added")

        # Display this simple test
        epd.display(epd.getbuffer(test_image))
        print("📺 Simple rectangle displayed - Check if you see a black square")
        time.sleep(5)

        # Test 2: Try text without font (should always work)
        print("📝 Test 2: Text without font...")
        text_image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(text_image)

        try:
            # Try to draw text with default font
            draw.text((20, 20), "TEST", fill=0)
            print("✅ Text added with default font")
        except Exception as e:
            print(f"❌ Text drawing failed: {e}")

        epd.display(epd.getbuffer(text_image))
        print("📺 Text test displayed - Check if you see 'TEST'")
        time.sleep(5)

        # Test 3: Try with explicit font loading
        print("🔤 Test 3: Loading font explicitly...")
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
            print("✅ Default font loaded successfully")

            font_image = Image.new('1', (width, height), 255)
            draw = ImageDraw.Draw(font_image)

            # Draw text multiple ways
            draw.text((20, 20), "HELLO", font=font, fill=0)
            draw.text((20, 50), font.getmask("WORLD"), fill=0)  # Alternative method

            epd.display(epd.getbuffer(font_image))
            print("📺 Font test displayed - Should see 'HELLO' and 'WORLD'")
            time.sleep(5)

        except Exception as e:
            print(f"❌ Font test failed: {e}")

        # Test 4: Manual pixel drawing (simulate text)
        print("🖌️ Test 4: Manual pixel drawing...")
        pixel_image = Image.new('1', (width, height), 255)
        pixels = pixel_image.load()

        # Draw letter 'A' manually with pixels
        letter_a = [
            [0,0,1,1,1,1,0,0],
            [0,1,0,0,0,0,1,0],
            [0,1,0,0,0,0,1,0],
            [0,1,1,1,1,1,1,0],
            [0,1,0,0,0,0,1,0],
            [0,1,0,0,0,0,1,0],
        ]

        start_x, start_y = 50, 100
        for y, row in enumerate(letter_a):
            for x, pixel in enumerate(row):
                if pixel == 1:
                    pixels[start_x + x, start_y + y] = 0

        print("✅ Manual 'A' drawn")
        epd.display(epd.getbuffer(pixel_image))
        print("📺 Manual 'A' displayed - You should see a pixelated letter 'A'")
        time.sleep(5)

        # Save all images for inspection
        test_image.save('debug_rectangle.png')
        text_image.save('debug_text.png')
        pixel_image.save('debug_manual.png')
        print("💾 All debug images saved")

        epd.sleep()
        print("✅ Debug completed")

        return True

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 TEXT RENDERING DEBUG")
    print("=" * 40)
    print("This test will show:")
    print("1. A black rectangle")
    print("2. Text with default font")
    print("3. Text with loaded font")
    print("4. Manually drawn letter 'A'")
    print()
    print("Tell me which ones you can see!")
    print("=" * 40)

    debug_text()