import requests

def fetch_weather(api_key, city):
    url = f"http://api.weatherapi.com/v1/current.json"
    params = {"key": api_key, "q": city, "aqi": "no"}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            weather_data = response.json()
            # Further validation can be added here
            return weather_data
        else:
            print(f"Error fetching weather data: HTTP {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    
