# from weather_api import fetch_weather
# from display import display_weather
import get_config
import os

def main():
    weather_api_key = get_config.get_config_value('WEATHER_API_KEY')
    city_api_key = get_config.get_config_value('CITY_API_KEY')
    print(weather_api_key,city_api_key)
    # Add additional logic here to use weather_api_key and city_api_key


if __name__ == '__main__':
    main()
