# from weather_api import fetch_weather
# from display import display_weather
import get_config
import get_weather
import get_poem

def main():
    weather_api_key = get_config.get_config_value('WEATHER_API_KEY')
    city_api_key = get_config.get_config_value('CITY_API_KEY')
    poem_token_api_url = get_config.get_config_value('POEM_TOKEN_API_URL')
    daily_poem_api_url = get_config.get_config_value('DAILY_POEM_API_URL')
    print(weather_api_key,city_api_key)
    # Add additional logic here to use weather_api_key and city_api_key
    weather = get_weather.fetch_weather(weather_api_key,city_api_key)
    poem_token_api = get_poem.get_token(poem_token_api_url)
    poem = get_poem.get_poem_detail(poem_token_api,daily_poem_api_url)
    print (weather)
    print (poem)


if __name__ == '__main__':
    main()
