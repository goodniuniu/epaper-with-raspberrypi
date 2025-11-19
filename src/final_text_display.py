#!/usr/bin/env python3
"""
Final Text Display Test
既然你能看到黑白切换，这个测试将显示清晰文本
"""

import sys
import os
import time

# Add e-paper library path
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

def final_text_test():
    """Final test to display clear text on working e-paper"""

    try:
        print("🎯 Final Text Display Test")
        print("=" * 40)

        import waveshare_epd.epd3in52 as epd3in52
        from PIL import Image, ImageDraw, ImageFont

        print("🔧 Importing libraries...")
        epd = epd3in52.EPD()
        epd.init()

        width, height = epd.width, epd.height
        print(f"📐 Display size: {width}x{height}")

        # Step 1: Clear to white background
        print("🧹 Clearing to white...")
        epd.Clear()
        time.sleep(3)

        # Step 2: Display large, clear text
        print("📝 Creating text display...")
        text_image = Image.new('1', (width, height), 255)  # White background
        draw = ImageDraw.Draw(text_image)

        # Use default font and make it extra clear
        font = ImageFont.load_default()

        # Draw border first
        draw.rectangle([5, 5, width-5, height-5], outline=0, width=2)

        # Add big text by drawing multiple times
        title_text = "HELLO"
        x_offset = 50
        y_offset = 30

        # Draw title multiple times for bold effect
        for dx in range(2):
            for dy in range(2):
                draw.text((x_offset+dx, y_offset+dy), title_text, font=font, fill=0)

        # Add weather info
        info_lines = [
            "City: GUANGZHOU",
            "Temp: 13.4 C",
            "Weather: Light Rain",
            "Time: " + time.strftime("%H:%M")
        ]

        y_pos = 80
        for line in info_lines:
            draw.text((15, y_pos), line, font=font, fill=0)
            y_pos += 25

        print("📺 Displaying text...")
        epd.display(epd.getbuffer(text_image))
        print("✅ Text displayed!")

        # Save the image
        text_image.save('final_text_display.png')
        print("💾 Image saved as 'final_text_display.png'")

        # Wait for you to see the result
        print("⏳ Display will remain for 10 seconds...")
        time.sleep(10)

        # Cleanup
        epd.sleep()
        print("✅ Test completed successfully!")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎉 CONGRATULATIONS! 🎉")
    print()
    print("Since you can see black/white switching,")
    print("your e-paper display is working!")
    print()
    print("This test will show clear text.")
    print("Watch your screen carefully...")
    print()

    success = final_text_test()

    if success:
        print()
        print("🎊 SUCCESS! 🎊")
        print()
        print("You should now see:")
        print("- A border around the screen")
        print("- 'HELLO' at the top")
        print("- Weather information")
        print("- Current time")
        print()
        print("Your e-paper display system is now working perfectly!")
        print("You can run the main application:")
        print()
        print("./run_display.sh")
        print()
        print("或者手动运行:")
        print("python src/fixed_main_display.py")
    else:
        print("Test failed - check error messages")