#!/usr/bin/env python3
"""
Pixel Test Only
只测试最基础的像素绘制，避免字体问题
"""

import sys
import os
import time

# Add e-paper library path
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

def pixel_test():
    """Test basic pixel drawing only"""

    try:
        print("🖌️ PIXEL TEST ONLY")
        print("=" * 30)

        import waveshare_epd.epd3in52 as epd3in52
        from PIL import Image

        print("✅ Libraries imported")

        epd = epd3in52.EPD()
        epd.init()

        width, height = epd.width, epd.height
        print(f"📐 Display size: {width}x{height}")

        # Test 1: Pure black screen
        print("⚫ Test 1: Pure black screen...")
        black_image = Image.new('1', (width, height), 0)  # All black
        epd.display(epd.getbuffer(black_image))
        print("✅ Black screen displayed - should see solid black")
        time.sleep(4)

        # Test 2: Pure white screen
        print("⚪ Test 2: Pure white screen...")
        white_image = Image.new('1', (width, height), 255)  # All white
        epd.display(epd.getbuffer(white_image))
        print("✅ White screen displayed - should see solid white")
        time.sleep(4)

        # Test 3: Half black, half white
        print("⚫⚪ Test 3: Half black, half white...")
        half_image = Image.new('1', (width, height), 255)  # White background
        pixels = half_image.load()

        # Make left half black
        for x in range(width // 2):
            for y in range(height):
                pixels[x, y] = 0

        epd.display(epd.getbuffer(half_image))
        print("✅ Half screen displayed - left black, right white")
        time.sleep(4)

        # Test 4: Checkerboard pattern
        print("♟️ Test 4: Checkerboard pattern...")
        check_image = Image.new('1', (width, height), 255)
        pixels = check_image.load()

        # Create checkerboard with 10x10 pixel squares
        square_size = 10
        for x in range(width):
            for y in range(height):
                if (x // square_size + y // square_size) % 2 == 0:
                    pixels[x, y] = 0

        epd.display(epd.getbuffer(check_image))
        print("✅ Checkerboard displayed - should see chess pattern")
        time.sleep(4)

        # Test 5: Cross pattern
        print("✚ Test 5: Cross pattern...")
        cross_image = Image.new('1', (width, height), 255)
        pixels = cross_image.load()

        # Draw a cross
        # Vertical line
        for y in range(height):
            pixels[width // 2, y] = 0
        # Horizontal line
        for x in range(width):
            pixels[x, height // 2] = 0

        # Make it thicker
        for y in range(height):
            pixels[width // 2 + 1, y] = 0
            pixels[width // 2 - 1, y] = 0
        for x in range(width):
            pixels[x, height // 2 + 1] = 0
            pixels[x, height // 2 - 1] = 0

        epd.display(epd.getbuffer(cross_image))
        print("✅ Cross displayed - should see a + symbol")
        time.sleep(4)

        # Save images
        black_image.save('test_black.png')
        white_image.save('test_white.png')
        half_image.save('test_half.png')
        check_image.save('test_check.png')
        cross_image.save('test_cross.png')

        print("💾 All test images saved")

        # Cleanup
        epd.sleep()
        print("✅ Pixel test completed!")

        return True

    except Exception as e:
        print(f"❌ Pixel test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🖌️ PIXEL TEST - NO TEXT")
    print("=" * 30)
    print("This will only test basic patterns:")
    print("1. All black screen")
    print("2. All white screen")
    print("3. Half black/white")
    print("4. Checkerboard")
    print("5. Cross pattern")
    print()
    print("If you see clear patterns, hardware is working!")
    print("If you see grey lines, there's a connection/power issue.")
    print("=" * 30)

    pixel_test()