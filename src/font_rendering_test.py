#!/usr/bin/env python3
"""
Font and Rendering Test for E-Paper Display
Tests different fonts and rendering styles for optimal e-paper display

This script creates various font tests to ensure text is readable
on the small e-paper screen with different character sets (English/Chinese).
"""

import logging
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_available_fonts() -> List[Tuple[str, ImageFont.FreeTypeFont]]:
    """
    Get list of available fonts for testing

    Returns:
        List of tuples with (font_name, font_object)
    """
    fonts = []

    # System fonts to try
    font_attempts = [
        # Standard system fonts
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVu Sans Bold"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVu Sans"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "Liberation Sans"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "Liberation Sans Bold"),
        ("/System/Library/Fonts/Arial.ttf", "Arial (macOS)"),
        ("C:/Windows/Fonts/arial.ttf", "Arial (Windows)"),
        ("arial.ttf", "Arial (local)"),
    ]

    # Try to load each font
    for font_path, font_name in font_attempts:
        try:
            if os.path.exists(font_path):
                font_obj = ImageFont.truetype(font_path, 18)
                fonts.append((font_name, font_obj))
                logger.info(f"✅ Loaded font: {font_name}")
            else:
                logger.debug(f"Font not found: {font_path}")
        except (OSError, IOError, AttributeError) as e:
            logger.debug(f"Failed to load {font_name}: {e}")

    # If no fonts loaded, use default
    if not fonts:
        default_font = ImageFont.load_default()
        fonts.append(("Default Font", default_font))
        logger.warning("⚠️ Using default font only")

    return fonts


def create_font_test_image() -> str:
    """
    Create comprehensive font test image

    Returns:
        Path to generated test image
    """
    # Image dimensions (matching e-paper display)
    width, height = 360, 480

    # Create white background
    image = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(image)

    # Get available fonts
    fonts = get_available_fonts()

    y_pos = 20
    line_height = 35

    # Title
    try:
        title_font = fonts[0][1] if fonts else ImageFont.load_default()
        draw.text((10, y_pos), "E-Paper Font Testing", font=title_font, fill=0)
    except:
        draw.text((10, y_pos), "E-Paper Font Testing", fill=0)

    y_pos += 50

    # Test each font with different text samples
    test_texts = [
        "The quick brown fox",
        "jumps over the lazy",
        "dog. ABCDEFGHIJKLMN",
        "Temperature: 25.3°C",
        "Weather: Light rain",
        "朝代：唐代",
        "作者：李白",
        "诗词：床前明月光",
        "疑是地上霜",
        "举头望明月",
        "低头思故乡",
    ]

    for font_name, font in fonts:
        draw.text((10, y_pos), f"{font_name}:", font=font, fill=0)
        y_pos += line_height

        # Test different text samples
        for i, text in enumerate(test_texts[:3]):  # Limit to 3 texts per font
            if y_pos + line_height > height - 50:
                break

            try:
                # Get text width for display
                if hasattr(font, 'getbbox'):
                    bbox = font.getbbox(text)
                    text_width = bbox[2]
                else:
                    text_width = len(text) * 8  # Rough estimate

                # Truncate if too wide
                max_width = width - 20
                if text_width > max_width:
                    trunc_len = int(len(text) * (max_width / text_width))
                    text = text[:trunc_len] + "..."

                draw.text((10, y_pos), text, font=font, fill=0)
                y_pos += line_height

            except Exception as e:
                logger.warning(f"Error rendering text with {font_name}: {e}")
                draw.text((10, y_pos), f"[Error: {str(e)[:20]}]", fill=0)
                y_pos += line_height

        y_pos += 15  # Space between fonts

        if y_pos > height - 100:
            break

    # Add footer with information
    y_pos = height - 40
    try:
        small_font = fonts[0][1] if fonts else ImageFont.load_default()
        draw.text((10, y_pos), f"Generated: {len(fonts)} fonts tested", font=small_font, fill=0)
    except:
        draw.text((10, y_pos), f"Generated: {len(fonts)} fonts tested", fill=0)

    # Save image
    output_path = "font_test_output.png"
    try:
        image.save(output_path)
        logger.info(f"Font test saved: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save font test: {e}")
        return ""


def create_layout_test() -> str:
    """
    Create layout test showing actual e-paper display layout

    Returns:
        Path to generated layout test image
    """
    width, height = 360, 480
    image = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(image)

    # Get best font available
    fonts = get_available_fonts()
    primary_font = fonts[0][1] if fonts else ImageFont.load_default()

    # Simulate actual e-paper layout
    y_pos = 10

    # Weather section
    draw.rectangle([5, y_pos, width-5, y_pos + 60], outline=0, width=1)
    draw.text((15, y_pos + 5), "Weather Section", font=primary_font, fill=0)
    y_pos += 25

    # Weather data simulation
    small_font = primary_font
    draw.text((15, y_pos), "Guangzhou: 22°C", font=small_font, fill=0)
    y_pos += 20
    draw.text((15, y_pos), "Condition: Partly cloudy", font=small_font, fill=0)
    y_pos += 50

    # Poetry section
    draw.rectangle([5, y_pos, width-5, y_pos + 200], outline=0, width=1)
    draw.text((15, y_pos + 5), "Poetry Section", font=primary_font, fill=0)
    y_pos += 30

    # Poetry content
    poem_lines = [
        "Title: 静夜思",
        "Author: 李白",
        "Dynasty: 唐代",
        "",
        "床前明月光，",
        "疑是地上霜。",
        "举头望明月，",
        "低头思故乡。",
    ]

    for line in poem_lines:
        draw.text((15, y_pos), line, font=small_font, fill=0)
        y_pos += 25

    # System section
    y_pos = height - 80
    draw.rectangle([5, y_pos, width-5, height-5], outline=0, width=1)
    draw.text((15, y_pos + 5), "System: IP 192.168.1.100", font=small_font, fill=0)
    y_pos += 25
    draw.text((15, y_pos), "Time: 15:58:30", font=small_font, fill=0)

    # Save layout test
    output_path = "layout_test_output.png"
    try:
        image.save(output_path)
        logger.info(f"Layout test saved: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save layout test: {e}")
        return ""


def run_font_tests():
    """Run comprehensive font and rendering tests"""
    logger.info("Starting font and rendering tests")

    # Test 1: Font rendering capabilities
    logger.info("Test 1: Font rendering capabilities")
    font_test_path = create_font_test_image()
    if font_test_path:
        logger.info(f"✅ Font test completed: {font_test_path}")

    # Test 2: Layout testing
    logger.info("Test 2: Layout testing")
    layout_test_path = create_layout_test()
    if layout_test_path:
        logger.info(f"✅ Layout test completed: {layout_test_path}")

    logger.info("🎉 Font and rendering tests completed!")
    logger.info("📸 Check generated PNG files for visual results")

    return font_test_path, layout_test_path


if __name__ == "__main__":
    try:
        font_path, layout_path = run_font_tests()
        if font_path and layout_path:
            print(f"\n🎉 Font tests completed successfully!")
            print(f"📸 Font test: {font_path}")
            print(f"📸 Layout test: {layout_path}")
            print(f"📋 These images show how text will render on your e-paper display")
        else:
            print(f"\n❌ Font tests had issues (see logs)")
    except Exception as e:
        print(f"\n❌ Font tests failed: {e}")
        logger.error(f"Font test failure: {e}")