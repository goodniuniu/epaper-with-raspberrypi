#!/usr/bin/env python3
"""
SPI Alternative Test
尝试不同的SPI设置来解决灰色条纹问题
"""

import sys
import os
import time

# Add e-paper library path
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

def test_spi_alternatives():
    """Test with different SPI configurations"""

    try:
        print("🔄 SPI ALTERNATIVE TEST")
        print("=" * 40)

        # Try to modify SPI settings before importing e-paper library
        print("⚙️ Attempting to configure SPI...")

        # Set up environment variables that might affect SPI
        os.environ['SPI_SPEED'] = '2000000'  # 2MHz
        os.environ['SPI_MODE'] = '0'

        print("✅ SPI environment configured")

        # Try alternative EPD initialization
        import waveshare_epd.epd3in52 as epd3in52
        from PIL import Image

        print("📦 Library imported successfully")

        # Create EPD instance
        epd = epd3in52.EPD()

        # Try manual initialization with more delay
        print("⚡ Manual initialization with delays...")
        time.sleep(1)  # Wait before init

        epd.init()
        time.sleep(1)  # Wait after init

        print("✅ Initialization completed")

        width, height = epd.width, epd.height
        print(f"📐 Display: {width}x{height}")

        # Test with very simple pattern first
        print("🧹 Simple clear test...")
        epd.Clear()
        time.sleep(3)  # Longer wait for clear
        print("✅ Clear completed")

        # Test with high contrast vertical stripes
        print("📊 Vertical stripes test...")
        stripe_image = Image.new('1', (width, height), 255)
        pixels = stripe_image.load()

        # Create wide vertical stripes (easier to render)
        stripe_width = 20
        for x in range(width):
            stripe_color = 0 if (x // stripe_width) % 2 == 0 else 255
            for y in range(height):
                pixels[x, y] = stripe_color

        print("📺 Displaying vertical stripes...")
        epd.display(epd.getbuffer(stripe_image))
        print("✅ Vertical stripes displayed")
        time.sleep(5)

        # Test with horizontal stripes
        print("📊 Horizontal stripes test...")
        h_stripe_image = Image.new('1', (width, height), 255)
        pixels = h_stripe_image.load()

        stripe_height = 20
        for y in range(height):
            stripe_color = 0 if (y // stripe_height) % 2 == 0 else 255
            for x in range(width):
                pixels[x, y] = stripe_color

        print("📺 Displaying horizontal stripes...")
        epd.display(epd.getbuffer(h_stripe_image))
        print("✅ Horizontal stripes displayed")
        time.sleep(5)

        # Test with large blocks (easiest pattern)
        print("🔲 Large block test...")
        block_image = Image.new('1', (width, height), 255)
        pixels = block_image.load()

        # Create 4 large blocks
        block_w, block_h = width // 2, height // 2
        blocks = [
            (0, 0, 0),                    # Top-left: black
            (block_w, 0, 255),            # Top-right: white
            (0, block_h, 255),            # Bottom-left: white
            (block_w, block_h, 0)         # Bottom-right: black
        ]

        for x_start, y_start, color in blocks:
            for x in range(x_start, min(x_start + block_w, width)):
                for y in range(y_start, min(y_start + block_h, height)):
                    pixels[x, y] = color

        print("📺 Displaying 4-block pattern...")
        epd.display(epd.getbuffer(block_image))
        print("✅ 4-block pattern displayed")
        time.sleep(5)

        # Save test images
        stripe_image.save('spi_vertical_stripes.png')
        h_stripe_image.save('spi_horizontal_stripes.png')
        block_image.save('spi_4blocks.png')

        print("💾 Test images saved")

        epd.sleep()
        print("✅ SPI alternative test completed!")

        return True

    except Exception as e:
        print(f"❌ SPI alternative test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_spi_settings():
    """Check current SPI settings"""
    print("🔍 Checking SPI settings...")

    try:
        # Check if SPI is enabled
        with open('/boot/config.txt', 'r') as f:
            config_content = f.read()
            if 'spi=on' in config_content:
                print("✅ SPI is enabled in config.txt")
            else:
                print("⚠️ SPI might not be enabled in config.txt")

        # Check SPI module
        result = os.system('lsmod | grep spi_bcm2835 > /dev/null')
        if result == 0:
            print("✅ SPI module loaded")
        else:
            print("⚠️ SPI module might not be loaded")

    except Exception as e:
        print(f"❌ Could not check SPI settings: {e}")

if __name__ == "__main__":
    print("🔄 SPI ALTERNATIVE TEST")
    print("=" * 40)
    print("Since your hardware worked before,")
    print("let's try alternative SPI settings...")
    print("=" * 40)

    # Check current settings
    check_spi_settings()
    print()

    # Run alternative test
    success = test_spi_alternatives()

    if success:
        print("\n✅ SPI alternative test completed!")
        print("Please tell me if you still see grey stripes")
        print("with these different patterns:")
        print("1. Wide vertical stripes")
        print("2. Wide horizontal stripes")
        print("3. Large 4-block pattern")
    else:
        print("\n❌ Test failed")