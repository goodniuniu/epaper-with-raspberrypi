import requests

def get_current_weather(api_key, city):
    url = f"http://api.weatherapi.com/v1/current.json?key=28962db3791a4792b4c90923241402&q=Guangzhou&aqi=no"
    response = requests.get(url)
    data = response.json()
    
    # 打印基本的天气信息
    print(f"City: {data['location']['name']}")
    print(f"Region: {data['location']['region']}")
    print(f"Country: {data['location']['country']}")
    print(f"Temperature (°C): {data['current']['temp_c']}")
    print(f"Condition: {data['current']['condition']['text']}")
    print(f"Humidity: {data['current']['humidity']}")
    print(f"Wind Speed (kph): {data['current']['wind_kph']}")
    print(f"Feels like (°C): {data['current']['feelslike_c']}")

# 替换以下字符串YOUR_API_KEY_HERE为你的WeatherAPI.com API密钥
api_key = "YOUR_API_KEY_HERE"
city = "Guangzhou"

get_current_weather(api_key, city)
