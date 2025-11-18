#!/usr/bin/env python3
"""
Modern E-paper Display Application
Updated: 2025-11-18

Main application for fetching weather and Chinese poetry data
for display on Raspberry Pi e-paper screen.
"""

import logging
from typing import Optional, Dict, Any
import get_config
import get_weather
import class_poem_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('epaper_app.log', mode='a')
    ]
)


def fetch_weather_data(weather_api_key: str, city: str) -> Optional[Dict[str, Any]]:
    """
    Fetch weather data from the API.

    Args:
        weather_api_key: Weather API key
        city: City name for weather data

    Returns:
        Weather data dictionary or None if failed
    """
    try:
        weather = get_weather.fetch_weather(weather_api_key, city)
        return weather
    except Exception as e:
        logging.error(f"Failed to fetch weather data: {e}")
        return None


def fetch_poem_data(token_url: str, daily_poem_url: str) -> Optional[class_poem_api.PoemAPI]:
    """
    Fetch poem data using the PoemAPI class.

    Args:
        token_url: URL to obtain API token
        daily_poem_url: URL to fetch daily poem

    Returns:
        PoemAPI instance with poem data or None if failed
    """
    try:
        poem_api = class_poem_api.PoemAPI(daily_poem_url, token_url)
        if poem_api.get_poem_detail():
            return poem_api
        else:
            return None
    except Exception as e:
        logging.error(f"Failed to fetch poem data: {e}")
        return None


def display_weather_info(weather: Optional[Dict[str, Any]]) -> None:
    """Display formatted weather information."""
    if weather:
        logging.info("Weather data retrieved successfully:")
        logging.info(f"Current temperature: {weather.get('current', {}).get('temp_c', 'N/A')}°C")
        logging.info(f"Condition: {weather.get('current', {}).get('condition', {}).get('text', 'N/A')}")
        logging.info(f"Location: {weather.get('location', {}).get('name', 'N/A')}")
    else:
        logging.warning("No weather data available")


def display_poem_info(poem_api: Optional[class_poem_api.PoemAPI]) -> None:
    """Display formatted poem information."""
    if poem_api:
        logging.info("Poem data retrieved successfully:")
        logging.info(f"Title: {poem_api.title or 'N/A'}")
        logging.info(f"Dynasty: {poem_api.dynasty or 'N/A'}")
        logging.info(f"Author: {poem_api.author or 'N/A'}")
        logging.info(f"Content preview: {poem_api.content or 'N/A'}")
        logging.info("Full poem content:")
        logging.info(poem_api.full_content or 'N/A')
    else:
        logging.warning("No poem data available")


def main() -> None:
    """Main application entry point."""
    logging.info("Starting E-paper Display Application")

    try:
        # Load configuration
        weather_api_key = get_config.get_config_value('WEATHER_API_KEY')
        city_api_key = get_config.get_config_value('CITY_API_KEY')
        poem_token_api_url = get_config.get_config_value('POEM_TOKEN_API_URL')
        daily_poem_api_url = get_config.get_config_value('DAILY_POEM_API_URL')

        logging.info(f"Configuration loaded. Target city: {city_api_key}")

        # Fetch weather data
        weather = fetch_weather_data(weather_api_key, city_api_key)
        display_weather_info(weather)

        # Fetch poem data using object-oriented approach
        poem_api = fetch_poem_data(poem_token_api_url, daily_poem_api_url)
        display_poem_info(poem_api)

        logging.info("Application completed successfully")

    except Exception as e:
        logging.error(f"Application failed: {e}")
        raise


if __name__ == '__main__':
    main()
