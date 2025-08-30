import logging
import requests
from pathlib import Path
import json

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class WordAPI:
    def __init__(self, word_api_url=None, sentence_api_url=None):
        """
        初始化每日单词API客户端
        
        参数:
        - word_api_url: 每日单词API地址
        - sentence_api_url: 每日长句API地址
        """
        # 使用免费的每日单词API
        self.word_api_url = word_api_url or "https://api.wordnik.com/v4/words.json/wordOfTheDay"
        self.sentence_api_url = sentence_api_url or "https://api.quotable.io/random"
        
        # 数据存储路径
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.word_file = self.data_dir / 'daily_word.json'
        self.sentence_file = self.data_dir / 'daily_sentence.json'
        
        # 确保数据目录存在
        self.data_dir.mkdir(exist_ok=True)
        
        # 初始化单词和句子属性
        self.word = None
        self.word_definition = None
        self.word_pronunciation = None
        self.word_example = None
        self.sentence = None
        self.sentence_author = None
        self.sentence_tags = None

    def get_daily_word(self):
        """
        获取每日单词及其详细信息
        
        返回:
        - bool: True表示成功获取，False表示失败
        """
        try:
            # 使用备用API - 每日英语单词
            backup_url = "https://api.dictionaryapi.dev/api/v2/entries/en/hello"  # 示例，实际可替换为每日单词服务
            
            # 这里使用一个简单的单词列表作为示例
            import random
            words_data = [
                {
                    "word": "serendipity",
                    "definition": "The occurrence and development of events by chance in a happy or beneficial way",
                    "pronunciation": "/ˌserənˈdipədē/",
                    "example": "A fortunate stroke of serendipity brought the two old friends together."
                },
                {
                    "word": "ephemeral",
                    "definition": "Lasting for a very short time",
                    "pronunciation": "/əˈfem(ə)rəl/",
                    "example": "The beauty of cherry blossoms is ephemeral, lasting only a few weeks."
                },
                {
                    "word": "mellifluous",
                    "definition": "Sweet or musical; pleasant to hear",
                    "pronunciation": "/məˈliflo͞oəs/",
                    "example": "Her mellifluous voice captivated the entire audience."
                },
                {
                    "word": "ubiquitous",
                    "definition": "Present, appearing, or found everywhere",
                    "pronunciation": "/yo͞oˈbikwədəs/",
                    "example": "Smartphones have become ubiquitous in modern society."
                },
                {
                    "word": "perspicacious",
                    "definition": "Having a ready insight into and understanding of things",
                    "pronunciation": "/ˌpərspəˈkāSHəs/",
                    "example": "The perspicacious detective quickly solved the complex case."
                }
            ]
            
            # 随机选择一个单词（实际应用中可以基于日期选择）
            import datetime
            today = datetime.date.today()
            word_index = today.toordinal() % len(words_data)
            word_data = words_data[word_index]
            
            # 更新类属性
            self.word = word_data['word']
            self.word_definition = word_data['definition']
            self.word_pronunciation = word_data['pronunciation']
            self.word_example = word_data['example']
            
            # 保存到文件
            self._save_word_data(word_data)
            
            logging.info(f"成功获取每日单词: {self.word}")
            return True
            
        except Exception as e:
            logging.error(f"获取每日单词时出错: {e}")
            # 尝试从本地文件加载
            return self._load_word_data()

    def get_daily_sentence(self):
        """
        获取每日励志长句
        
        返回:
        - bool: True表示成功获取，False表示失败
        """
        try:
            response = requests.get(self.sentence_api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 更新类属性
            self.sentence = data.get('content', '')
            self.sentence_author = data.get('author', 'Unknown')
            self.sentence_tags = data.get('tags', [])
            
            # 保存到文件
            sentence_data = {
                'sentence': self.sentence,
                'author': self.sentence_author,
                'tags': self.sentence_tags,
                'date': str(datetime.date.today())
            }
            self._save_sentence_data(sentence_data)
            
            logging.info(f"成功获取每日句子: {self.sentence[:50]}...")
            return True
            
        except requests.RequestException as e:
            logging.error(f"获取每日句子时出错: {e}")
            # 尝试从本地文件加载
            return self._load_sentence_data()
        except Exception as e:
            logging.error(f"处理每日句子数据时出错: {e}")
            return self._load_sentence_data()

    def _save_word_data(self, word_data):
        """保存单词数据到文件"""
        try:
            import datetime
            word_data['date'] = str(datetime.date.today())
            with self.word_file.open('w', encoding='utf-8') as f:
                json.dump(word_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存单词数据时出错: {e}")

    def _save_sentence_data(self, sentence_data):
        """保存句子数据到文件"""
        try:
            with self.sentence_file.open('w', encoding='utf-8') as f:
                json.dump(sentence_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存句子数据时出错: {e}")

    def _load_word_data(self):
        """从文件加载单词数据"""
        try:
            if self.word_file.exists():
                with self.word_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.word = data.get('word')
                    self.word_definition = data.get('definition')
                    self.word_pronunciation = data.get('pronunciation')
                    self.word_example = data.get('example')
                    logging.info("从本地文件加载单词数据")
                    return True
        except Exception as e:
            logging.error(f"加载本地单词数据时出错: {e}")
        return False

    def _load_sentence_data(self):
        """从文件加载句子数据"""
        try:
            if self.sentence_file.exists():
                with self.sentence_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sentence = data.get('sentence')
                    self.sentence_author = data.get('author')
                    self.sentence_tags = data.get('tags', [])
                    logging.info("从本地文件加载句子数据")
                    return True
        except Exception as e:
            logging.error(f"加载本地句子数据时出错: {e}")
        return False

    def get_daily_content(self):
        """
        获取每日完整内容（单词+句子）
        
        返回:
        - bool: True表示至少获取了一项内容，False表示全部失败
        """
        word_success = self.get_daily_word()
        sentence_success = self.get_daily_sentence()
        
        return word_success or sentence_success

    def format_display_content(self):
        """
        格式化显示内容，适合墨水屏显示
        
        返回:
        - str: 格式化后的显示内容
        """
        content_lines = []
        
        # 添加标题
        content_lines.append("=== Daily Word & Quote ===")
        content_lines.append("")
        
        # 添加单词部分
        if self.word:
            content_lines.append("📚 Word of the Day:")
            content_lines.append(f"   {self.word.upper()}")
            if self.word_pronunciation:
                content_lines.append(f"   {self.word_pronunciation}")
            content_lines.append("")
            
            if self.word_definition:
                content_lines.append("Definition:")
                # 自动换行处理长定义
                definition_words = self.word_definition.split()
                line = "   "
                for word in definition_words:
                    if len(line + word) > 35:  # 适合墨水屏的行宽
                        content_lines.append(line)
                        line = "   " + word + " "
                    else:
                        line += word + " "
                if line.strip():
                    content_lines.append(line)
                content_lines.append("")
            
            if self.word_example:
                content_lines.append("Example:")
                # 自动换行处理长例句
                example_words = self.word_example.split()
                line = "   "
                for word in example_words:
                    if len(line + word) > 35:
                        content_lines.append(line)
                        line = "   " + word + " "
                    else:
                        line += word + " "
                if line.strip():
                    content_lines.append(line)
                content_lines.append("")
        
        # 添加分隔线
        content_lines.append("-" * 30)
        content_lines.append("")
        
        # 添加句子部分
        if self.sentence:
            content_lines.append("💭 Quote of the Day:")
            content_lines.append("")
            
            # 自动换行处理长句子
            sentence_words = self.sentence.split()
            line = "   \""
            for word in sentence_words:
                if len(line + word) > 33:  # 为引号留空间
                    content_lines.append(line)
                    line = "   " + word + " "
                else:
                    line += word + " "
            if line.strip():
                content_lines.append(line.rstrip() + "\"")
            content_lines.append("")
            
            if self.sentence_author:
                content_lines.append(f"   — {self.sentence_author}")
                content_lines.append("")
        
        # 添加日期
        import datetime
        content_lines.append(f"Date: {datetime.date.today().strftime('%Y-%m-%d')}")
        
        return "\n".join(content_lines)

    def get_summary(self):
        """
        获取内容摘要
        
        返回:
        - dict: 包含单词和句子信息的字典
        """
        return {
            'word': {
                'text': self.word,
                'definition': self.word_definition,
                'pronunciation': self.word_pronunciation,
                'example': self.word_example
            },
            'sentence': {
                'text': self.sentence,
                'author': self.sentence_author,
                'tags': self.sentence_tags
            }
        }