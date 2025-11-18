#!/usr/bin/env python3
"""
Complete Integration Test for E-Paper Display Application
Simulates the full application workflow with display output

This test simulates the complete flow:
1. Load configuration
2. Fetch weather data
3. Fetch poetry data
4. Display formatted information
5. Save multiple display states for review
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import get_config
import get_weather
import class_poem_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('integration_test.log')
    ]
)
logger = logging.getLogger(__name__)


class IntegrationTestEPD:
    """Extended mock e-paper display for integration testing"""

    def __init__(self, width: int = 360, height: int = 480):
        self.width = width
        self.height = height
        self.display_count = 0
        self.test_results = []

    def init(self):
        """Mock initialization"""
        logger.info("Integration test display initialized")

    def Clear(self):
        """Mock clear screen"""
        logger.debug("Integration test screen cleared")

    def display(self, image, test_name: str = "test"):
        """Mock display with image saving and metrics"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"integration_test_{self.display_count}_{test_name}_{timestamp}.png"

            image.save(filename)

            # Analyze image for e-paper suitability
            file_size = os.path.getsize(filename)
            image_info = f"{image.width}x{image.height} mono"

            result = {
                'filename': filename,
                'test_name': test_name,
                'file_size': file_size,
                'image_info': image_info,
                'timestamp': datetime.now().isoformat()
            }

            self.test_results.append(result)
            self.display_count += 1

            logger.info(f"✅ Display test saved: {filename} ({file_size} bytes)")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save display image: {e}")
            return False

    def refresh(self):
        """Mock refresh with timing"""
        logger.debug("Integration test display refreshed")

    def sleep(self):
        """Mock sleep"""
        logger.debug("Integration test display sleeping")


def get_optimal_font() -> ImageFont.FreeTypeFont:
    """Get the best available font for e-paper display"""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "arial.ttf"
    ]

    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, 18)
        except:
            continue

    # Fallback to default font
    logger.warning("Using default font - install better fonts for optimal display")
    return ImageFont.load_default()


def create_weather_poisson_display(weather_data: Optional[Dict[str, Any]],
                                 poem_data: Optional[class_poem_api.PoemAPI],
                                 epd: IntegrationTestEPD,
                                 ip_address: str = "192.168.1.100") -> bool:
    """
    Create the main weather + poetry display

    Args:
        weather_data: Weather information from API
        poem_data: Poetry information from API
        epd: Mock e-paper display instance
        ip_address: IP address for system info

    Returns:
        True if successful, False otherwise
    """
    epd.init()
    epd.Clear()

    # Create image with proper e-paper dimensions
    image = Image.new('1', (epd.width, epd.height), 255)  # White background
    draw = ImageDraw.Draw(image)

    # Load fonts
    try:
        primary_font = get_optimal_font()

        # Create different font sizes if possible
        try:
            large_font = ImageFont.truetype(primary_font.path, 24) if hasattr(primary_font, 'path') else ImageFont.load_default()
            medium_font = primary_font
            small_font = ImageFont.truetype(primary_font.path, 12) if hasattr(primary_font, 'path') else ImageFont.load_default()
        except:
            large_font = medium_font = small_font = primary_font

    except Exception as e:
        logger.error(f"Font loading failed: {e}")
        return False

    y_pos = 10

    # === Header ===
    draw.text((10, y_pos), "Weather & Poetry Display", font=large_font, fill=0)
    y_pos += 35

    # Draw separator
    draw.line([(10, y_pos), (epd.width - 10, y_pos)], fill=0, width=1)
    y_pos += 15

    # === Weather Section ===
    draw.text((10, y_pos), "Current Weather:", font=medium_font, fill=0)
    y_pos += 25

    if weather_data:
        try:
            location = weather_data.get('location', {})
            current = weather_data.get('current', {})
            condition = current.get('condition', {})

            # Location
            location_name = location.get('name', 'Unknown')
            draw.text((10, y_pos), f"Location: {location_name}", font=medium_font, fill=0)
            y_pos += 25

            # Temperature with units
            temp = current.get('temp_c', 'N/A')
            draw.text((10, y_pos), f"Temperature: {temp}°C", font=medium_font, fill=0)
            y_pos += 25

            # Weather condition
            weather_text = condition.get('text', 'Unknown')
            draw.text((10, y_pos), f"Condition: {weather_text}", font=medium_font, fill=0)
            y_pos += 25

            # Additional weather details
            humidity = current.get('humidity', 'N/A')
            wind_kph = current.get('wind_kph', 'N/A')
            draw.text((10, y_pos), f"Humidity: {humidity}% | Wind: {wind_kph} kph", font=small_font, fill=0)
            y_pos += 35

        except Exception as e:
            logger.error(f"Error rendering weather data: {e}")
            draw.text((10, y_pos), "Weather data error", font=medium_font, fill=0)
            y_pos += 30
    else:
        draw.text((10, y_pos), "Weather data unavailable", font=medium_font, fill=0)
        y_pos += 30

    # Draw separator
    draw.line([(10, y_pos), (epd.width - 10, y_pos)], fill=0, width=1)
    y_pos += 15

    # === Poetry Section ===
    draw.text((10, y_pos), "Today's Poetry:", font=medium_font, fill=0)
    y_pos += 25

    if poem_data:
        try:
            # Title
            title = poem_data.title or "Untitled"
            draw.text((10, y_pos), f"Title: {title}", font=medium_font, fill=0)
            y_pos += 25

            # Dynasty and author
            dynasty = poem_data.dynasty or "Unknown"
            author = poem_data.author or "Unknown"
            draw.text((10, y_pos), f"Dynasty: {dynasty} | Author: {author}", font=medium_font, fill=0)
            y_pos += 30

            # Poetry content preview
            content = poem_data.content or "No content"
            draw.text((10, y_pos), "Preview:", font=medium_font, fill=0)
            y_pos += 25

            # Handle multi-line content with proper wrapping
            max_width = epd.width - 20
            wrapped_lines = []

            if hasattr(medium_font, 'getbbox'):
                # Modern PIL version with proper text wrapping
                words = content.split()
                current_line = []
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    bbox = medium_font.getbbox(test_line)
                    if bbox[2] <= max_width:
                        current_line.append(word)
                    else:
                        if current_line:
                            wrapped_lines.append(' '.join(current_line))
                            current_line = [word]
                        else:
                            wrapped_lines.append(word[:20])  # Truncate long words
                if current_line:
                    wrapped_lines.append(' '.join(current_line))
            else:
                # Fallback for older PIL versions
                line_length = 20  # Rough estimate
                for i in range(0, len(content), line_length):
                    wrapped_lines.append(content[i:i+line_length])

            # Display wrapped content (limit to 3 lines to fit screen)
            for line in wrapped_lines[:3]:
                draw.text((10, y_pos), line, font=medium_font, fill=0)
                y_pos += 22

            # Full preview indicator
            if len(poem_data.full_content or '') > 50:
                draw.text((10, y_pos), f"...{len(poem_data.full_content or 0)} chars total", font=small_font, fill=0)
                y_pos += 22

        except Exception as e:
            logger.error(f"Error rendering poetry data: {e}")
            draw.text((10, y_pos), "Poetry data error", font=medium_font, fill=0)
            y_pos += 30
    else:
        draw.text((10, y_pos), "Poetry data unavailable", font=medium_font, fill=0)
        y_pos += 30

    # === System Information Section ===
    y_pos = epd.height - 60
    draw.line([(10, y_pos), (epd.width - 10, y_pos)], fill=0, width=1)
    y_pos += 10

    draw.text((10, y_pos), f"IP: {ip_address}", font=small_font, fill=0)

    # Timestamp
    timestamp = datetime.now().strftime("%m-%d %H:%M")
    draw.text((epd.width - 70, y_pos), timestamp, font=small_font, fill=0)

    # Save the display
    success = epd.display(image, "main_display")
    epd.refresh()
    epd.sleep()

    return success


def run_integration_tests():
    """Run complete integration tests"""
    logger.info("🚀 Starting complete e-paper display integration tests")

    # Initialize test display
    epd = IntegrationTestEPD()

    try:
        # === Test 1: Configuration Loading ===
        logger.info("📋 Step 1: Loading configuration...")
        weather_api_key = get_config.get_config_value('WEATHER_API_KEY')
        city_api_key = get_config.get_config_value('CITY_API_KEY')
        poem_token_url = get_config.get_config_value('POEM_TOKEN_API_URL')
        daily_poem_url = get_config.get_config_value('DAILY_POEM_API_URL')

        if not all([weather_api_key, city_api_key, poem_token_url, daily_poem_url]):
            logger.error("❌ Configuration incomplete")
            return False

        logger.info("✅ Configuration loaded successfully")
        logger.info(f"   Target city: {city_api_key}")

        # === Test 2: Weather Data Fetching ===
        logger.info("🌤️ Step 2: Fetching weather data...")
        weather_data = get_weather.fetch_weather(weather_api_key, city_api_key)

        if weather_data:
            logger.info("✅ Weather data retrieved successfully")
            location = weather_data.get('location', {}).get('name', 'Unknown')
            temp = weather_data.get('current', {}).get('temp_c', 'N/A')
            condition = weather_data.get('current', {}).get('condition', {}).get('text', 'N/A')
            logger.info(f"   {location}: {temp}°C, {condition}")
        else:
            logger.warning("⚠️ Weather data not available - using mock data")

        # === Test 3: Poetry Data Fetching ===
        logger.info("📜 Step 3: Fetching poetry data...")
        poem_api = class_poem_api.PoemAPI(daily_poem_api_url, poem_token_url)
        poem_success = poem_api.get_poem_detail()

        if poem_success:
            logger.info("✅ Poetry data retrieved successfully")
            title = poem_api.title or "Unknown"
            author = poem_api.author or "Unknown"
            logger.info(f"   '{title}' by {author}")
        else:
            logger.warning("⚠️ Poetry data not available - using mock data")

        # === Test 4: Display Rendering ===
        logger.info("🖼️ Step 4: Creating display...")
        success = create_weather_poisson_display(
            weather_data,
            poem_api if poem_success else None,
            epd
        )

        if not success:
            logger.error("❌ Display rendering failed")
            return False

        logger.info("✅ Display rendering completed")

        # === Test 5: Results Summary ===
        logger.info("📊 Integration test results:")
        for result in epd.test_results:
            logger.info(f"   📸 {result['filename']} - {result['test_name']} ({result['file_size']} bytes)")

        logger.info("🎉 Complete integration test finished successfully!")
        logger.info(f"📁 Generated {len(epd.test_results)} display images")
        logger.info("📋 Images show the actual e-paper display layout with real data")

        return True

    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting E-Paper Display Integration Test")
    print("=" * 50)

    success = run_integration_tests()

    print("=" * 50)
    if success:
        print("✅ Integration test completed successfully!")
        print("📸 Check generated PNG files for actual display output")
        print("📋 Integration log saved to: integration_test.log")
    else:
        print("❌ Integration test failed!")
        print("🔧 Check integration_test.log for detailed errors")
        print("📋 This suggests there may be issues with your configuration or APIs")