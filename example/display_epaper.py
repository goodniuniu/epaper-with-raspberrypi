import requests
import sqlite3
import os,sys,time
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import logging
from waveshare_epd import epd3in52
import text_wrap
import get_ipaddress

def save_poem_to_db(poem_data, db_path='poems.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO poems (title, dynasty, author, content, full_content)
        VALUES (?, ?, ?, ?, ?)
    ''', (poem_data['title'], poem_data['dynasty'], poem_data['author'], poem_data['content'], poem_data['full_content']))
    print("writing to db")
    conn.commit()
    conn.close()


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



def get_token(api_url):
    """
    请求API以获取Token，并将Token存储到文件系统中。
    
    参数:
    - api_url: 获取Token的API的URL。
    
    返回:
    - token: 获取到的Token。
    """
    try:
        # 发起GET请求获取Token
        response = requests.get(api_url)
        if response.status_code == 200:
            # 解析JSON数据获取Token
            token = response.json()['data']
            # 将Token存储到文件中
            with open('token.txt', 'w') as file:
                file.write(token)
            return token
        else:
            print(f"请求Token失败，状态码：{response.status_code}")
            return None
    except Exception as e:
        print(f"请求Token时出错: {e}")
        return None

def load_token():
    """
    从文件系统中加载Token。
    
    返回:
    - token: 文件中存储的Token，如果文件不存在则为None。
    """
    if os.path.exists('token.txt'):
        with open('token.txt', 'r') as file:
            token = file.read().strip()
        return token
    else:
        return None

def get_daily_poem(api_url, token):
    """
    使用Token请求API以获取每日一句古诗词及其详细信息。
    
    参数:
    - api_url: 获取每日古诗词的API的URL。
    - token: 之前获取并存储的Token。
    
    返回:
    - poem_details: 包含古诗词详细信息的字典。
    """
    headers = {'X-User-Token': token}
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            poem_details = {
                'content': data['content'],  # 每日一句古诗词
                'title': data['origin']['title'],  # 诗的标题
                'dynasty': data['origin']['dynasty'],  # 朝代
                'author': data['origin']['author'],  # 作者
                'full_content': '\n'.join(data['origin']['content']),  # 整首诗的内容
                #'translate': '\n'.join(data['origin']['translate']) if 'translate' in data['origin'] else None  # 译文（如果有的话）
            }
            return poem_details
        else:
            print(f"请求每日古诗词失败，状态码：{response.status_code}")
            return None
    except Exception as e:
        print(f"请求每日古诗词时出错: {e}")
        return None


def get_poem_data():
    token_api_url = 'https://v2.jinrishici.com/token'
    daily_poem_api_url = 'https://v2.jinrishici.com/sentence'
    
    # 尝试从文件中加载Token
    token = load_token()
    print (token)
    if not token:
        # 如果没有Token，则获取新的Token
        token = get_token(token_api_url)        
    if token:
        # 使用Token获取每日古诗词
        poem = get_daily_poem(daily_poem_api_url, token)
        if poem:
            print(f"今日古诗词：{poem}")
            return poem
        else:
            print("无法获取每日古诗词。")
    else:
        print("无法获取Token。")
        
        
def display_poem_on_epaper():

    poem = get_poem_data()
    save_poem_to_db(poem)
     # 初始化电子墨水屏、设置字体等
    epd = epd3in52.EPD()
    epd.init()
    epd.Clear()
    image = Image.new('1', (epd.width,epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    
        
    # poem content
    draw.text((10, 80), f"今日诗词: {poem['content']} ", font=font, fill=0)
    
    # poem title
    
    # poem dynasty
    
    # poem author
    
    # poem full_content
        
    # 显示图像
    epd.display(epd.getbuffer(image))
    epd.refresh()
    time.sleep(2)
    epd.sleep()

def display_on_epaper():
    ## 获取天气相关信息和图片
    weather_data = get_weather_data()  # 确保这个函数获取了最新的天气数据
    resized_icon = download_and_resize_icon(weather_data['current']['condition']['icon'],size=(32,32))
    ## 获取每日诗歌相关信息
    poem = get_poem_data()
    save_poem_to_db(poem)
    poem_title = text_wrap.format_poem_for_display(poem['title'],360)
    poem_author = text_wrap.format_poem_for_display(poem['author'],360)
    poem_dynasty = text_wrap.format_poem_for_display(poem['dynasty'],360)
    poem_content = text_wrap.format_poem_for_display(poem['content'],360)
    poem_text = text_wrap.format_poem_for_display(poem['full_content'],360)
    
    # 获得本地的ipaddress，方便远程运维
    ipaddress = get_ipaddress.get_ip_address()
    
    
    # 初始化电子墨水屏、设置字体等
    epd = epd3in52.EPD()
    epd.init()
    epd.Clear()
    image = Image.new('1', (epd.width,epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font12 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 12)
    
    # 绘制温度信息
    draw.text((10, 10), f"当前气温: {weather_data['current']['temp_c']} C", font=font18, fill=0)
    
    # 绘制天气条件文本，正确访问天气数据
    draw.text((10, 30), f"今日天气: {weather_data['current']['condition']['text']}", font=font18, fill=0)
    image.paste(resized_icon, (200, 15))
     # poem content
    draw.text((10, 70), f"此刻诗词: ", font=font18, fill=0)
    draw.text((10, 90), f"《{poem_title}》 ", font=font18, fill=0)
    draw.text((10, 110), f"朝代：{poem_dynasty} ", font=font18, fill=0)
    draw.text((10, 130), f"作者：{poem_author} ", font=font18, fill=0)
    draw.text((10, 160), f"{poem_content} ", font=font24, fill=0)
    
    # 显示ipaddress
    draw.text((80, 330), f"my ipaddress: {ipaddress}", font=font12, fill=0)
    # 显示图像
    epd.display(epd.getbuffer(image))
    epd.refresh()
    time.sleep(2)
    epd.sleep()
    

try:
    # display_weather_on_epaper()
    display_on_epaper()
except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd3in52.epdconfig.module_exit(cleanup=True)
    exit()
