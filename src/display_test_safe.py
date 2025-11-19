#!/usr/bin/env python3
"""
Safe E-Paper Display Test
Tests display functionality without requiring actual hardware

This script simulates e-paper display operations and creates output images
to verify that the weather and poetry data formatting looks correct.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
import get_config
import get_weather
import class_poem_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockEPD:
    """Mock e-paper display for testing without hardware"""

    def __init__(self, width: int = 360, height: int = 480):
        self.width = width
        self.height = height
        logger.info(f"Mock e-paper initialized: {width}x{height}px")

    def init(self):
        """Mock initialization"""
        logger.info("Mock display initialized")

    def Clear(self):
        """Mock clear screen"""
        logger.info("Mock screen cleared")

    def display(self, buffer):
        """Mock display - saves image instead"""
        try:
            # Save the buffer as an image file for inspection
            image_path = "display_test_output.png"
            if hasattr(buffer, 'image'):
                buffer.image.save(image_path)
                logger.info(f"Display test saved as: {image_path}")
            else:
                logger.warning("Could not save display image")
        except Exception as e:
            logger.error(f"Error saving display image: {e}")

    def refresh(self):
        """Mock refresh"""
        logger.info("Mock display refreshed")

    def sleep(self):
        """Mock sleep"""
        logger.info("Mock display sleeping")


def create_test_display(weather_data: Optional[Dict[str, Any]],
                       poem_data: Optional[class_poem_api.PoemAPI],
                       ip_address: str = "192.168.1.100") -> MockEPD:
    """
    Create and test display with weather and poetry data

    Args:
        weather_data: Weather information dictionary
        poem_data: PoemAPI instance with poem information
        ip_address: IP address for display

    Returns:
        MockEPD instance for testing
    """
    # Initialize mock display
    epd = MockEPD()
    epd.init()
    epd.Clear()

    # Create image
    image = Image.new('1', (epd.width, epd.height), 255)  # White background
    draw = ImageDraw.Draw(image)

    # Try to load fonts, fall back to default if not available
    try:
        # Try system fonts first
        font24 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font18 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font12 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except (OSError, IOError):
        try:
            # Fallback to Arial on other systems
            font24 = ImageFont.truetype("arial.ttf", 24) if os.path.exists("arial.ttf") else ImageFont.load_default()
            font18 = ImageFont.truetype("arial.ttf", 18) if os.path.exists("arial.ttf") else ImageFont.load_default()
            font12 = ImageFont.truetype("arial.ttf", 12) if os.path.exists("arial.ttf") else ImageFont.load_default()
        except (OSError, IOError):
            # Use default font
            font24 = font18 = font12 = ImageFont.load_default()
            logger.warning("Using default font - install proper fonts for better display")

    # Draw weather section
    y_pos = 10
    draw.text((10, y_pos), "E-PAPER DISPLAY TEST", font=font18 if font18 else font24, fill=0)
    y_pos += 30

    # Weather information
    if weather_data:
        location = weather_data.get('location', {})
        current = weather_data.get('current', {})

        draw.text((10, y_pos), f"Weather for {location.get('name', 'Unknown')}:",
                 font=font18, fill=0)
        y_pos += 25

        temp = current.get('temp_c', 'N/A')
        condition = current.get('condition', {}).get('text', 'N/A')
        humidity = current.get('humidity', 'N/A')

        draw.text((10, y_pos), f"Temperature: {temp}°C", font=font18, fill=0)
        y_pos += 25
        draw.text((10, y_pos), f"Condition: {condition}", font=font18, fill=0)
        y_pos += 25
        draw.text((10, y_pos), f"Humidity: {humidity}%", font=font18, fill=0)
        y_pos += 30
    else:
        draw.text((10, y_pos), "Weather data unavailable", font=font18, fill=0)
        y_pos += 30

    # Draw separator line
    draw.line([(10, y_pos), (epd.width - 10, y_pos)], fill=0, width=1)
    y_pos += 20

    # Poetry information
    draw.text((10, y_pos), "Today's Poetry:", font=font18, fill=0)
    y_pos += 30

    if poem_data:
        title = poem_data.title or "Unknown"
        dynasty = poem_data.dynasty or "Unknown"
        author = poem_data.author or "Unknown"
        content = poem_data.content or "No content"

        draw.text((10, y_pos), f"Title: {title}", font=font18, fill=0)
        y_pos += 25
        draw.text((10, y_pos), f"Dynasty: {dynasty}", font=font18, fill=0)
        y_pos += 25
        draw.text((10, y_pos), f"Author: {author}", font=font18, fill=0)
        y_pos += 25
        draw.text((10, y_pos), f"Content:", font=font18, fill=0)
        y_pos += 25

        # Handle multi-line content
        max_line_width = epd.width - 20
        try:
            lines = []
            if font18.getbbox:
                # Modern PIL version
                words = content.split()
                current_line = []
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    bbox = font18.getbbox(test_line)
                    if bbox[2] < max_line_width:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                        else:
                            lines.append(word)
                if current_line:
                    lines.append(' '.join(current_line))
            else:
                # Older PIL version - simple split
                lines = [content[i:i+30] for i in range(0, len(content), 30)]

            for line in lines[:5]:  # Limit to 5 lines
                draw.text((10, y_pos), line, font=font18, fill=0)
                y_pos += 20

        except Exception as e:
            draw.text((10, y_pos), str(content)[:50], font=font18, fill=0)
            y_pos += 25
    else:
        draw.text((10, y_pos), "Poetry data unavailable", font=font18, fill=0)
        y_pos += 30

    # Draw IP address
    y_pos = epd.height - 30
    draw.text((10, y_pos), f"IP Address: {ip_address}", font=font12, fill=0)

    # Draw timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((epd.width - 150, y_pos), f"Test: {timestamp}", font=font12, fill=0)

    # Save the display state to image
    epd.image = image  # Store for saving
    return epd


def test_display_functionality():
    """Test complete display functionality"""
    logger.info("Starting e-paper display functionality test")

    try:
        # Load configuration
        weather_api_key = get_config.get_config_value('WEATHER_API_KEY')
        city_api_key = get_config.get_config_value('CITY_API_KEY')
        poem_token_url = get_config.get_config_value('POEM_TOKEN_API_URL')
        daily_poem_url = get_config.get_config_value('DAILY_POEM_API_URL')

        logger.info("Configuration loaded successfully")

        # Fetch weather data
        weather_data = get_weather.fetch_weather(weather_api_key, city_api_key)
        if weather_data:
            logger.info("✅ Weather data retrieved successfully")
        else:
            logger.warning("⚠️ Weather data not available")

        # Fetch poetry data
        poem_api = class_poem_api.PoemAPI(daily_poem_url, poem_token_url)
        poem_success = poem_api.get_poem_detail()
        if poem_success:
            logger.info("✅ Poetry data retrieved successfully")
        else:
            logger.warning("⚠️ Poetry data not available")

        # Create test display
        logger.info("Creating display test...")
        epd = create_test_display(weather_data, poem_api if poem_success else None)

        # Mock display operations
        epd.display(epd)
        epd.refresh()

        logger.info("✅ Display test completed successfully")
        logger.info("📸 Check display_test_output.png for visual results")

        return True

    except Exception as e:
        logger.error(f"❌ Display test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_display_functionality()
    if success:
        print("\n🎉 E-Paper display test completed successfully!")
        print("📸 Generated display_test_output.png")
        print("📋 The image shows how your display would look with real data")
    else:
        print("\n❌ E-Paper display test failed!")
        print("🔧 Check logs for error details")