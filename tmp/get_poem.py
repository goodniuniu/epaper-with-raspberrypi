# {"status":"success","data":"VSAWXgNXS5eUaDjhjZd4AN3XXeue+54O"}
import requests
import os
import textwrap
import logging

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
            logging.error(f"Failed to get token, status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        logging.error(f"Error getting token: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error getting token: {e}")
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


def format_poem_for_display(poem_data, max_width=20):
    """
    Formats the poem data for display, wrapping text as needed.
    
    :param poem_data: Dictionary containing poem details.
    :param max_width: Maximum line width for text wrapping.
    :return: Formatted string ready for display.
    """
    # Header information
    header = f"{poem_data['title']} - {poem_data['author']} ({poem_data['dynasty']})"
    wrapped_header = "\n".join(textwrap.wrap(header, width=max_width))
    
    # Poem content
    content_lines = poem_data['full_content'].split('\n')
    wrapped_content = []
    for line in content_lines:
        wrapped_lines = textwrap.wrap(line, width=max_width)
        wrapped_content.extend(wrapped_lines or [""])
    
    formatted_poem = wrapped_header + "\n\n" + "\n".join(wrapped_content)
    return formatted_poem

# Example usage
poem_data = {
    'content': '风前横笛斜吹雨，醉里簪花倒著冠。',
    'title': '鹧鸪天·座中有眉山隐客史应之和前韵即席答之',
    'dynasty': '宋代',
    'author': '黄庭坚',
    'full_content': '黄菊枝头生晓寒。人生莫放酒杯干。风前横笛斜吹雨，醉里簪花倒著冠。\n身健在，且加餐。舞裙歌板尽清欢。黄花白发相牵挽，付与时人冷眼看。'
}
poem_data = get_poem_data()
formatted_poem = format_poem_for_display(poem_data, max_width=10)  # Adjust `max_width` as needed for your display

print(formatted_poem)
# Now you would use your display_text function to render `formatted_poem` on your e-ink display


# 注意：在实际使用中请取消以下行的注释来运行主函数
# get_poem_data()
