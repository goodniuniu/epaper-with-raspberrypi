import requests
import os
import logging
from pathlib import Path
import process_poem_db_sql

import os
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 获取当前文件所在目录的路径（src 目录）
current_directory = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录的路径
project_directory = os.path.dirname(current_directory)

# 构建 token.txt 文件的路径
TOKEN_FILE = os.path.join(project_directory, 'data', 'token.txt')
logging.info(TOKEN_FILE)

# try:
#     with open(token_file_path, 'r') as file:
#         token = file.read().strip()
# except FileNotFoundError:
#     print("Token file not found. Please make sure the file exists.")

def load_token():
    try:
        with open(TOKEN_FILE, 'r') as file:
            token = file.read().strip()
        return token
    except FileNotFoundError:
        logging.error("Token file not found.")
        return None
    except Exception as e:
        logging.error(f"Error loading token: {e}")
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
            logging.error(f"Failed to get daily poem, status code: {response.status_code}")
            return None
    except (requests.RequestException, ValueError) as e:
        logging.error(f"Error getting daily poem: {e}")
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
        try:
            # 发起GET请求获取Token
            response = requests.get(api_url)
            response.raise_for_status()  # 在状态码非200时抛出异常
            data = response.json()
            if 'data' in data:
                token = data['data']
                logging.info(token)
                # 将Token存储到文件中
                with open(TOKEN_FILE, 'w') as file:
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

    