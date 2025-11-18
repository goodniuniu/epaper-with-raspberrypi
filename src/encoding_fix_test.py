#!/usr/bin/env python3
"""
Test script to fix Chinese character encoding issues in PIL/Pillow
"""

import sys
import os

# Add e-paper library path
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

from PIL import Image, ImageDraw, ImageFont

def test_chinese_text():
    """Test rendering Chinese text with PIL"""

    # Create a simple test image
    width, height = 400, 200
    image = Image.new('1', (width, height), 255)  # White background
    draw = ImageDraw.Draw(image)

    # Test text samples
    test_texts = [
        "English Text Test",
        "晓出净慈寺送林子方",  # Chinese poem title
        "杨万里",  # Author name in Chinese
        "接天莲叶无穷碧",  # First line of poem
        "映日荷花别样红",  # Second line of poem
    ]

    y_pos = 10
    try:
        # Try to use a better font if available
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font = ImageFont.load_default()

    print("Testing text rendering...")

    for text in test_texts:
        try:
            print(f"Rendering: {text}")
            # Ensure text is properly encoded as UTF-8
            if isinstance(text, str):
                # Python 3 strings are already Unicode
                text_to_render = text
            else:
                # Convert bytes to string if needed
                text_to_render = text.decode('utf-8', errors='replace')

            draw.text((10, y_pos), text_to_render, font=font, fill=0)
            y_pos += 25

        except Exception as e:
            print(f"Error rendering '{text}': {e}")
            # Try with ASCII fallback
            ascii_text = text.encode('ascii', errors='replace').decode('ascii')
            draw.text((10, y_pos), ascii_text, font=font, fill=0)
            y_pos += 25

    # Save the test image
    try:
        image.save('encoding_test_output.png')
        print("✅ Test image saved as 'encoding_test_output.png'")
        return True
    except Exception as e:
        print(f"❌ Failed to save image: {e}")
        return False

if __name__ == "__main__":
    print("🔤 Chinese Text Encoding Test")
    print("=" * 40)
    success = test_chinese_text()

    if success:
        print("✅ Encoding test completed successfully!")
    else:
        print("❌ Encoding test failed!")