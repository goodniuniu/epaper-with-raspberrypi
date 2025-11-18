import logging
from pathlib import Path
from typing import Optional, Dict, Any
import requests

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PoemAPI:
    def __init__(self, api_url: str, token_url: str, token_file: str = '../data/token.txt') -> None:
        self.api_url = api_url
        self.token_url = token_url
        self.token_file = Path(token_file)
        self.token = self.load_token()
        # 初始化诗歌详情属性
        self.title = None
        self.dynasty = None
        self.author = None
        self.content = None
        self.full_content = None
    
    def get_token(self) -> Optional[str]:
        """
        Request API token and store it in the file system.

        Returns:
            Optional[str]: The obtained token or None if failed.
        """
        try:
            # 发起GET请求获取Token
            response = requests.get(self.token_url)
            response.raise_for_status()
            token = response.json()['data']
            # 将Token存储到文件中
            with self.token_file.open('w') as file:
                file.write(token)
            return token
        except requests.RequestException as e:
            logging.error(f"请求Token时出错: {e}")
            return None

    
    def load_token(self) -> Optional[str]:
        """
        Load token from file, or obtain new token if file doesn't exist.

        Returns:
            Optional[str]: The loaded token or None if failed.
        """
        if self.token_file.exists():
            return self.token_file.read_text().strip()
        else:
            token = self.get_token()
            if token:
                return token
        return None

    def get_poem_detail(self) -> bool:
        """
        Request daily poem API to get poem details and update class attributes.

        Returns:
            bool: True if successfully obtained and updated details, False otherwise.
        """
        headers = {'X-User-Token': self.token}
        try:
            response = requests.get(self.api_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'data' in data:
                # 更新类属性
                self.title = data['data'].get('origin', {}).get('title')
                self.dynasty = data['data'].get('origin', {}).get('dynasty')
                self.author = data['data'].get('origin', {}).get('author')
                self.content = data['data'].get('content')
                self.full_content = '\n'.join(data['data'].get('origin', {}).get('content', []))
                return True  # 返回True表示成功获取并更新了详情
        except requests.RequestException as e:
            logging.error(f"请求每日古诗词时出错: {e}")
        return False  # 返回False表示获取详情失败

    def update_token(self, new_token: str) -> None:
        """
        Update token and write the new token to file.

        Args:
            new_token: The new token to store.
        """
        try:
            self.token = new_token
            with self.token_file.open('w') as file:
                file.write(new_token)
        except Exception as e:
            logging.error(f"更新Token时出错: {e}")

