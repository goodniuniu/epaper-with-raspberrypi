import requests
import os,sys,time
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import logging
from waveshare_epd import epd3in52


def get_weather_data():
    url = "http://api.weatherapi.com/v1/current.json?key=28962db3791a4792b4c90923241402&q=Guangzhou&aqi=no"
    response = requests.get(url)
    weather_data = response.json()
    return weather_data




def download_and_resize_icon(icon_url, size=(64, 64)):
    if not icon_url.startswith(('http:', 'https:')):
        icon_url = 'https:' + icon_url  # 确保URL具有协议前缀
    response = requests.get(icon_url)
    icon_image = Image.open(BytesIO(response.content))
    resized_icon = icon_image.resize(size, Image.Resampling.LANCZOS)  # 使用Image.Resampling.LANCZOS替代Image.ANTIALIAS
    return resized_icon

# 这个部分需要根据您实际使用的电子墨水屏库进行调整
def display_weather_on_epaper():
    weather_data = get_weather_data()  # 确保这个函数获取了最新的天气数据
    resized_icon = download_and_resize_icon(weather_data['current']['condition']['icon'],size=(32,32))
    
    # 初始化电子墨水屏、设置字体等
    epd = epd3in52.EPD()
    epd.init()
    epd.Clear()
    image = Image.new('1', (epd.width,epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    
    # 绘制温度信息
    draw.text((10, 10), f"当前气温: {weather_data['current']['temp_c']} C", font=font, fill=0)
    
    # 绘制天气条件文本，正确访问天气数据
    draw.text((10, 30), f"今日天气: {weather_data['current']['condition']['text']}", font=font, fill=0)
    image.paste(resized_icon, (200, 15))
    
    # 显示图像
    epd.display(epd.getbuffer(image))
    epd.refresh()
    time.sleep(2)
    epd.sleep()


try:
    display_weather_on_epaper()
except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd3in52.epdconfig.module_exit(cleanup=True)
    exit()
