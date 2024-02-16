import requests
import os
import json
from pathlib import Path
import process_poem_db_sql

import os

# 获取当前工作目录的路径
current_directory = os.getcwd()

# 构建 token.txt 文件的路径
TOKEN_FILE = os.path.join(current_directory, 'data', 'token.txt')

# try:
#     with open(token_file_path, 'r') as file:
#         token = file.read().strip()
# except FileNotFoundError:
#     print("Token file not found. Please make sure the file exists.")



def load_token():
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return None


def get_poem_from_url(api_url, token):
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
        else:
            print(f"请求每日古诗词失败，状态码：{response.status_code}")
            return None
    except (requests.RequestException, ValueError) as e:
        print(f"请求每日古诗词时出错: {e}")
        return None

def get_poem_details_from_db(content,db='poems.db'):
    id = process_poem_db_sql.find_poem_id_by_context(content)
    poem = process_poem_db_sql.read_poem_from_db(id)
    if poem:
        poem_details = {
                'content': poem[4],
                'title': poem[1],
                'dynasty': poem[2],
                'author': poem[3],
                'full_content': '\n'.join(poem[5]),
            }
    return poem_details   

def get_token(api_url):
    token = load_token()
    if token:
        return token
    else:
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
                
                # 修改get_token函数中的文件操作部分
                with TOKEN_FILE.open('w') as file:
                    file.write(token)
                return token
            else:
                print(f"请求Token失败，状态码：{response.status_code}")
                return None
        except Exception as e:
            print(f"请求Token时出错: {e}")
            return None

    