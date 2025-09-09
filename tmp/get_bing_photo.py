import requests
import json

def fetch_bing_daily_image():
    url = "https://bing.biturl.top/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        image_url = data['url']
        return image_url
    else:
        return None
    
from PIL import Image
import requests
from io import BytesIO

def process_image(image_url):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    
    # 调整图片大小以适应墨水屏尺寸，这里假设为400x300
    image = image.resize((192, 108))
    
    # 转换为黑白色
    image = image.convert('1')
    
    # 保存加工后的图片
    image.save('bing_daily_image.bmp')

    return image

# 假设image_url是从前面的函数中获取的


image_url = fetch_bing_daily_image()
print("Bing Daily Image URL:", image_url)

if image_url:
    processed_image = process_image(image_url)
    print("Image has been processed and saved.")
