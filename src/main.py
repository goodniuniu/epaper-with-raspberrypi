# from weather_api import fetch_weather
# from display import display_weather
import get_config
import get_weather
# import get_poem
import class_poem_api
import logging
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("main.py running")
    weather_api_key = get_config.get_config_value('WEATHER_API_KEY')
    city_api_key = get_config.get_config_value('CITY_API_KEY')
    poem_token_api_url = get_config.get_config_value('POEM_TOKEN_API_URL')
    daily_poem_api_url = get_config.get_config_value('DAILY_POEM_API_URL')
    # Add additional logic here to use weather_api_key and city_api_key
    weather = get_weather.fetch_weather(weather_api_key,city_api_key)
    print (weather)
    
    #基于面向过程的调用，如果需要测试可以采用。
    #poem_token_api = get_poem.get_token(poem_token_api_url)
    #poem = get_poem.get_poem_from_url(daily_poem_api_url,poem_token_api)
    #print (poem)
    

    # 基于面向对象方式获取诗歌详情，将作为主要方法
    # 创建PoemAPI类的实例
    ## 测试来源：
    # api_url = "https://v2.jinrishici.com/sentence"
    # token_url = "https://v2.jinrishici.com/token"

    poem_api = class_poem_api.PoemAPI(daily_poem_api_url, poem_token_api_url)
    # 获取诗歌详情
    if poem_api.get_poem_detail():
        logging.info("诗歌详情获取成功:")
        logging.info(f"标题: {poem_api.title}")
        logging.info(f"朝代: {poem_api.dynasty}")
        logging.info(f"作者: {poem_api.author}")
        logging.info("内容:")
        logging.info(poem_api.full_content)
    else:
        logging.error("获取诗歌详情失败")
    
if __name__ == '__main__':
    main()
