import requests
import os
import json
from functools import lru_cache

@lru_cache(maxsize=32)
def get_daily_poem(api_url, token):
    headers = {'X-User-Token': token}
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()  # 会在状态码非200时抛出异常
        data = response.json()
        if 'data' in data:
            poem_details = {
                'content': data['data'].get('content'),
                'title': data['data'].get('origin', {}).get('title'),
                'dynasty': data['data'].get('origin', {}).get('dynasty'),
                'author': data['data'].get('origin', {}).get('author'),
                'full_content': '\n'.join(data['data'].get('origin', {}).get('content', [])),
            }
            return poem_details
        return None
    except (requests.RequestException, ValueError) as e:
        print(f"请求每日古诗词时出错: {e}")
        return None


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
    