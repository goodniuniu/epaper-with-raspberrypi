import os
import configparser

def get_config_value(key_name):
    """Retrieve a configuration value for a given key."""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
    config.read(config_path)
    return config['DEFAULT'].get(key_name)


# Usage examples:
# weather_api_key = get_config_value('WEATHER_API_KEY')
# city_api_key = get_config_value('CITY_API_KEY')

