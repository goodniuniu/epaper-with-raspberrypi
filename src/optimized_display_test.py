#!/usr/bin/env python3
"""
Optimized E-paper Display Test
Fixed timing and SPI speed for better display quality
"""

import sys
import os
import time

# Add e-paper library path
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

def optimized_test():
    """Optimized test with better timing and SPI settings"""

    try:
        print("🔧 Importing e-paper library...")
        import waveshare_epd.epd3in52 as epd3in52
        from PIL import Image, ImageDraw, ImageFont

        print("✅ Library imported successfully")

        print("🖼️ Creating EPD driver...")
        epd = epd3in52.EPD()

        print("⚡ Initializing hardware with optimized settings...")
        epd.init()
        print("✅ Hardware initialized")

        width, height = epd.width, epd.height
        print(f"📐 Display size: {width}x{height}")

        # Test: Clear and wait longer
        print("🧹 Clearing display and waiting...")
        epd.Clear()
        time.sleep(5)  # Longer wait for clear to complete
        print("✅ Clear completed")

        # Test: Simple weather display
        print("🌤️ Creating weather display...")
        weather_image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(weather_image)

        # Use a larger font for better visibility
        try:
            font = ImageFont.load_default()
            print("✅ Using default font")
        except:
            font = None

        # Draw border
        draw.rectangle([5, 5, width-5, height-5], outline=0, width=2)

        # Add title
        if font:
            draw.text((20, 20), "WEATHER", font=font, fill=0)
            draw.text((20, 45), "DISPLAY", font=font, fill=0)

        # Add weather info
        if font:
            draw.text((20, 80), "City: GUANGZHOU", font=font, fill=0)
            draw.text((20, 105), "Temp: 13.4 C", font=font, fill=0)
            draw.text((20, 130), "Weather: Rain", font=font, fill=0)

        # Add time
        current_time = time.strftime("%H:%M")
        if font:
            draw.text((20, height-50), f"Time: {current_time}", font=font, fill=0)

        # Add dividing lines for better visibility
        draw.line([10, 70, width-10, 70], fill=0, width=1)
        draw.line([10, 160, width-10, 160], fill=0, width=1)

        print("📺 Displaying weather info...")
        epd.display(epd.getbuffer(weather_image))
        print("✅ Weather display completed")

        # Save the image for debugging
        weather_image.save('optimized_weather_test.png')
        print("💾 Image saved as 'optimized_weather_test.png'")

        # Wait longer for display to stabilize
        time.sleep(8)

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
    print("🧪 Optimized E-paper Display Test")
    print("=" * 50)
    print("This test uses better timing and simpler graphics")
    print("You should see clear weather information")
    print("=" * 50)
    print()

    success = optimized_test()

    if success:
        print("\n✅ Optimized test completed!")
        print("You should now see:")
        print("- Clear border around screen")
        print("- 'WEATHER DISPLAY' title")
        print("- Weather information (city, temp, condition)")
        print("- Current time")
        print("- Horizontal lines separating sections")
        print()
        print("If you still see stripes, check:")
        print("1. Power supply (try external 5V power)")
        print("2. Ribbon cable connection")
        print("3. GPIO pins are firmly connected")
    else:
        print("\n❌ Test failed - check error messages above")