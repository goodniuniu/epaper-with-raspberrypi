import logging
from typing import Optional, Dict, Any
import requests

# Module-level logger
logger = logging.getLogger(__name__)


def fetch_weather(api_key: str, city: str) -> Optional[Dict[str, Any]]:
    """
    Fetch weather data from WeatherAPI.

    Args:
        api_key: WeatherAPI authentication key
        city: City name for weather data

    Returns:
        Optional[Dict[str, Any]]: Weather data dictionary or None if failed
    """
    if not api_key:
        logger.error("Weather API key is required")
        return None

    if not city:
        logger.error("City name is required")
        return None

    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": city,
        "aqi": "no",
        "lang": "en"  # Explicit language setting
    }

    try:
        logger.info(f"Fetching weather for {city}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raises exception for 4XX/5XX status codes

        weather_data = response.json()

        # Validate response structure
        if not weather_data or 'current' not in weather_data:
            logger.error("Invalid weather data structure received")
            return None

        logger.info(f"Successfully fetched weather data for {city}")
        return weather_data

    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching weather data for {city}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while fetching weather data for {city}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching weather data for {city}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed while fetching weather data for {city}: {e}")
        return None
    except (ValueError, KeyError) as e:
        logger.error(f"Data parsing error for {city}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching weather data for {city}: {e}")
        return None

    
