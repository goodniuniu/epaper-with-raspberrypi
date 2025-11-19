#!/usr/bin/env python3
"""
Grey Lines Fix for E-paper Display
专门解决灰色纹路问题的显示测试
"""

import sys
import os
import time

# Add e-paper library path
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

def fix_grey_lines():
    """Test to fix grey lines and improve display quality"""

    try:
        print("🔧 Importing e-paper library...")
        import waveshare_epd.epd3in52 as epd3in52
        from PIL import Image, ImageDraw, ImageFont

        print("✅ Library imported successfully")

        print("🖼️ Creating EPD driver...")
        epd = epd3in52.EPD()

        print("⚡ Initializing hardware...")
        epd.init()
        print("✅ Hardware initialized")

        width, height = epd.width, epd.height
        print(f"📐 Display size: {width}x{height}")

        # Test 1: Multiple clear cycles to remove residual image
        print("🧹 Running multiple clear cycles...")
        for i in range(3):
            print(f"Clear cycle {i+1}/3...")
            epd.Clear()
            time.sleep(3)  # Wait 3 seconds between clears
        print("✅ Multiple clears completed")

        # Test 2: Full refresh with high contrast image
        print("⚫ Creating high contrast test...")
        high_contrast = Image.new('1', (width, height), 255)  # White
        draw = ImageDraw.Draw(high_contrast)

        # Create very clear, bold patterns
        # Large black rectangles for maximum contrast
        draw.rectangle([20, 20, 100, 100], fill=0)  # Big black square
        draw.rectangle([140, 20, 220, 100], fill=0)  # Another big square
        draw.rectangle([20, 140, 100, 220], fill=0)  # Bottom left
        draw.rectangle([140, 140, 220, 220], fill=0)  # Bottom right

        # Add thick lines
        draw.line([10, height//2, width-10, height//2], fill=0, width=3)
        draw.line([width//2, 10, width//2, height-10], fill=0, width=3)

        print("📺 Displaying high contrast pattern...")
        epd.display(epd.getbuffer(high_contrast))
        print("✅ High contrast displayed")
        time.sleep(5)

        # Test 3: Simple bold text
        print("📝 Creating bold text test...")
        text_image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(text_image)

        try:
            font = ImageFont.load_default()
            print("✅ Font loaded")
        except:
            font = None

        # Draw text multiple times for better contrast
        if font:
            for x in range(3):
                for y in range(3):
                    draw.text((10+x, 10+y), "TEST", font=font, fill=0)
            draw.text((10, 40), "88888888", font=font, fill=0)  # Numbers for clarity
            draw.text((10, 70), "########", font=font, fill=0)  # Symbols

        print("📺 Displaying bold text...")
        epd.display(epd.getbuffer(text_image))
        print("✅ Bold text displayed")
        time.sleep(5)

        # Test 4: Final clear and refresh
        print("🧹 Final clear and refresh...")
        epd.Clear()
        time.sleep(4)

        # Create clean weather display
        print("🌤️ Creating clean weather display...")
        clean_image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(clean_image)

        # Simple, clean design
        if font:
            draw.text((15, 15), "Weather:", font=font, fill=0)
            draw.text((15, 40), "City: Guangzhou", font=font, fill=0)
            draw.text((15, 65), "Temp: 13.4C", font=font, fill=0)
            draw.text((15, 90), "Rain", font=font, fill=0)

            # Add current time
            current_time = time.strftime("%H:%M")
            draw.text((15, 140), f"Time: {current_time}", font=font, fill=0)

        epd.display(epd.getbuffer(clean_image))
        print("✅ Clean weather display completed")
        time.sleep(5)

        # Save images for debugging
        high_contrast.save('high_contrast_test.png')
        text_image.save('bold_text_test.png')
        clean_image.save('clean_weather_display.png')
        print("💾 Debug images saved")

        # Final cleanup
        print("😴 Putting display to sleep...")
        epd.sleep()
        print("✅ All tests completed successfully!")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Grey Lines Fix Test")
    print("=" * 50)
    print("This test will:")
    print("1. Run multiple clear cycles")
    print("2. Display high contrast patterns")
    print("3. Show bold text")
    print("4. Final clean weather display")
    print("=" * 50)
    print()

    success = fix_grey_lines()

    if success:
        print("\n✅ Grey lines fix completed!")
        print("You should now see:")
        print("- Clear high contrast patterns (no grey lines)")
        print("- Bold, readable text")
        print("- Clean weather information")
        print()
        print("If you still see grey lines:")
        print("1. Try running this test 2-3 times")
        print("2. Check if the screen needs more time to stabilize")
        print("3. The screen might need a 'break-in' period")
    else:
        print("\n❌ Fix test failed - check error messages")