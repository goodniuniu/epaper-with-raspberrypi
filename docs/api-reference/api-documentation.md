# API 参考文档

## 📋 概述

本文档详细描述了每日单词墨水屏显示系统的API接口、配置选项和扩展方法。

## 🔌 核心API类

### WordAPI 类

每日单词API客户端，负责从外部API获取单词和句子数据。

#### 初始化

```python
from src.class_word_api import WordAPI

# 使用默认配置
api = WordAPI()

# 使用自定义配置
api = WordAPI(config_override={
    'word_api_url': 'https://custom-api.com/word',
    'sentence_api_url': 'https://custom-api.com/quote'
})
```

#### 方法

##### `get_daily_content() -> bool`

获取每日单词和句子内容。

**返回值：**
- `True`: 成功获取内容
- `False`: 获取失败

**示例：**
```python
api = WordAPI()
success = api.get_daily_content()
if success:
    print("内容获取成功")
    print(f"单词: {api.word_data}")
    print(f"句子: {api.sentence_data}")
```

##### `get_word_of_day() -> dict`

获取每日单词数据。

**返回值：**
```python
{
    'word': str,           # 单词
    'phonetic': str,       # 音标
    'definition': str,     # 定义
    'example': str,        # 例句
    'part_of_speech': str, # 词性
    'difficulty': str      # 难度级别
}
```

##### `get_daily_sentence() -> dict`

获取每日励志句子。

**返回值：**
```python
{
    'sentence': str,    # 句子内容
    'author': str,      # 作者
    'category': str,    # 分类
    'length': int       # 字符长度
}
```

##### `save_to_cache(data: dict, cache_type: str) -> bool`

保存数据到本地缓存。

**参数：**
- `data`: 要保存的数据字典
- `cache_type`: 缓存类型 ('word' 或 'sentence')

**返回值：**
- `True`: 保存成功
- `False`: 保存失败

##### `load_from_cache(cache_type: str) -> dict`

从本地缓存加载数据。

**参数：**
- `cache_type`: 缓存类型 ('word' 或 'sentence')

**返回值：**
- 缓存的数据字典，如果不存在则返回空字典

### EPaperDisplay 类

墨水屏显示控制器，负责内容渲染和显示。

#### 初始化

```python
from src.epaper_display_rpi import EPaperDisplay

# 使用默认配置
display = EPaperDisplay()

# 使用自定义配置
display = EPaperDisplay(config_override={
    'epaper_model': '2in13_V3',
    'font_size_word': 24,
    'font_size_definition': 16
})
```

#### 方法

##### `display_content(word_data: dict, sentence_data: dict) -> bool`

显示单词和句子内容到墨水屏。

**参数：**
- `word_data`: 单词数据字典
- `sentence_data`: 句子数据字典

**返回值：**
- `True`: 显示成功
- `False`: 显示失败

**示例：**
```python
word_data = {
    'word': 'serendipity',
    'phonetic': '/ˌserənˈdipədē/',
    'definition': 'The occurrence of events by chance in a happy way',
    'example': 'A fortunate stroke of serendipity brought them together.'
}

sentence_data = {
    'sentence': 'The best way to predict the future is to create it.',
    'author': 'Peter Drucker'
}

display = EPaperDisplay()
success = display.display_content(word_data, sentence_data)
```

##### `clear_display() -> bool`

清空墨水屏显示。

**返回值：**
- `True`: 清空成功
- `False`: 清空失败

##### `create_image(word_data: dict, sentence_data: dict) -> PIL.Image`

创建要显示的图像对象。

**参数：**
- `word_data`: 单词数据字典
- `sentence_data`: 句子数据字典

**返回值：**
- PIL图像对象

##### `format_text(text: str, max_width: int, font: PIL.ImageFont) -> list`

格式化文本以适应指定宽度。

**参数：**
- `text`: 要格式化的文本
- `max_width`: 最大宽度（像素）
- `font`: 字体对象

**返回值：**
- 格式化后的文本行列表

## ⚙️ 配置选项

### 主配置文件 (word_config.py)

#### API配置

```python
# API端点配置
WORD_API_CONFIG = {
    'word_api_url': 'https://api.wordnik.com/v4/words.json/wordOfTheDay',
    'word_api_key': 'your_api_key_here',
    'sentence_api_url': 'https://api.quotable.io/random',
    'timeout': 10,
    'retry_count': 3,
    'retry_delay': 2
}

# 备用API配置
FALLBACK_APIS = {
    'word_apis': [
        'https://api.wordnik.com/v4/words.json/wordOfTheDay',
        'https://api.urbandictionary.com/v0/random'
    ],
    'sentence_apis': [
        'https://api.quotable.io/random',
        'https://zenquotes.io/api/random'
    ]
}
```

#### 显示配置

```python
# 墨水屏配置
EPAPER_CONFIG = {
    'model': '2in13_V3',        # 墨水屏型号
    'width': 250,               # 屏幕宽度
    'height': 122,              # 屏幕高度
    'rotation': 0,              # 旋转角度 (0, 90, 180, 270)
    'color_mode': 'BW'          # 颜色模式 ('BW', 'BWR')
}

# 字体配置
FONT_CONFIG = {
    'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    'font_size_word': 20,       # 单词字体大小
    'font_size_phonetic': 14,   # 音标字体大小
    'font_size_definition': 12, # 定义字体大小
    'font_size_example': 10,    # 例句字体大小
    'font_size_sentence': 11,   # 句子字体大小
    'font_size_author': 9,      # 作者字体大小
    'line_spacing': 2           # 行间距
}

# 布局配置
LAYOUT_CONFIG = {
    'margin_top': 5,
    'margin_bottom': 5,
    'margin_left': 5,
    'margin_right': 5,
    'section_spacing': 8,
    'word_section_height': 60,
    'sentence_section_height': 50
}
```

#### 系统配置

```python
# 更新配置
UPDATE_CONFIG = {
    'update_times': ['08:00', '12:00', '18:00'],  # 更新时间
    'update_interval': 3600,    # 更新间隔（秒）
    'max_retries': 3,          # 最大重试次数
    'retry_interval': 300,     # 重试间隔（秒）
    'use_local_fallback': True # 使用本地备用内容
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'file_path': 'data/daily_word.log',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}

# 缓存配置
CACHE_CONFIG = {
    'word_cache_file': 'data/word_cache.json',
    'sentence_cache_file': 'data/sentence_cache.json',
    'cache_expiry': 86400,     # 缓存过期时间（秒）
    'max_cache_size': 100      # 最大缓存条目数
}
```

### 备用内容配置

```python
# 本地备用单词库
FALLBACK_WORDS = [
    {
        'word': 'serendipity',
        'phonetic': '/ˌserənˈdipədē/',
        'definition': 'The occurrence of events by chance in a happy way',
        'example': 'A fortunate stroke of serendipity brought them together.',
        'part_of_speech': 'noun',
        'difficulty': 'advanced'
    },
    {
        'word': 'ephemeral',
        'phonetic': '/əˈfem(ə)rəl/',
        'definition': 'Lasting for a very short time',
        'example': 'The beauty of cherry blossoms is ephemeral.',
        'part_of_speech': 'adjective',
        'difficulty': 'intermediate'
    }
    # ... 更多单词
]

# 本地备用句子库
FALLBACK_SENTENCES = [
    {
        'sentence': 'The best way to predict the future is to create it.',
        'author': 'Peter Drucker',
        'category': 'motivation'
    },
    {
        'sentence': 'Innovation distinguishes between a leader and a follower.',
        'author': 'Steve Jobs',
        'category': 'leadership'
    }
    # ... 更多句子
]
```

## 🔧 扩展开发

### 自定义API适配器

创建自定义API适配器来支持新的数据源：

```python
# src/custom_api_adapter.py
from abc import ABC, abstractmethod
import requests
import logging

class APIAdapter(ABC):
    """API适配器基类"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    def fetch_data(self):
        """获取数据的抽象方法"""
        pass
    
    def make_request(self, url, params=None, headers=None):
        """通用HTTP请求方法"""
        try:
            response = requests.get(
                url, 
                params=params, 
                headers=headers,
                timeout=self.config.get('timeout', 10)
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"API请求失败: {e}")
            return None

class CustomWordAPI(APIAdapter):
    """自定义单词API适配器"""
    
    def fetch_data(self):
        """获取单词数据"""
        url = self.config['api_url']
        headers = {'Authorization': f"Bearer {self.config['api_key']}"}
        
        data = self.make_request(url, headers=headers)
        if data:
            return self.transform_data(data)
        return None
    
    def transform_data(self, raw_data):
        """转换API数据格式"""
        return {
            'word': raw_data.get('word', ''),
            'phonetic': raw_data.get('pronunciation', ''),
            'definition': raw_data.get('meaning', ''),
            'example': raw_data.get('example_sentence', ''),
            'part_of_speech': raw_data.get('pos', ''),
            'difficulty': raw_data.get('level', 'intermediate')
        }

# 使用自定义适配器
config = {
    'api_url': 'https://your-custom-api.com/word',
    'api_key': 'your_api_key',
    'timeout': 15
}

adapter = CustomWordAPI(config)
word_data = adapter.fetch_data()
```

### 自定义显示主题

创建自定义显示主题：

```python
# src/custom_theme.py
from PIL import Image, ImageDraw, ImageFont

class CustomTheme:
    """自定义显示主题"""
    
    def __init__(self, config):
        self.config = config
        self.width = config['width']
        self.height = config['height']
    
    def create_layout(self, word_data, sentence_data):
        """创建自定义布局"""
        image = Image.new('1', (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)
        
        # 绘制背景装饰
        self.draw_background(draw)
        
        # 绘制单词部分
        y_offset = self.draw_word_section(draw, word_data, 10)
        
        # 绘制分隔线
        self.draw_separator(draw, y_offset)
        
        # 绘制句子部分
        self.draw_sentence_section(draw, sentence_data, y_offset + 10)
        
        return image
    
    def draw_background(self, draw):
        """绘制背景装饰"""
        # 绘制边框
        draw.rectangle([0, 0, self.width-1, self.height-1], outline=0)
        
        # 绘制角落装饰
        corner_size = 10
        for x, y in [(0, 0), (self.width-corner_size, 0), 
                     (0, self.height-corner_size), 
                     (self.width-corner_size, self.height-corner_size)]:
            draw.rectangle([x, y, x+corner_size, y+corner_size], outline=0)
    
    def draw_word_section(self, draw, word_data, y_start):
        """绘制单词部分"""
        font_word = ImageFont.truetype(self.config['font_path'], 18)
        font_phonetic = ImageFont.truetype(self.config['font_path'], 12)
        font_definition = ImageFont.truetype(self.config['font_path'], 10)
        
        y = y_start
        
        # 绘制单词
        word = word_data.get('word', '').upper()
        draw.text((10, y), word, font=font_word, fill=0)
        y += 22
        
        # 绘制音标
        phonetic = word_data.get('phonetic', '')
        if phonetic:
            draw.text((10, y), phonetic, font=font_phonetic, fill=0)
            y += 16
        
        # 绘制定义
        definition = word_data.get('definition', '')
        if definition:
            lines = self.wrap_text(definition, self.width - 20, font_definition)
            for line in lines:
                draw.text((10, y), line, font=font_definition, fill=0)
                y += 12
        
        return y
    
    def draw_separator(self, draw, y):
        """绘制分隔线"""
        draw.line([(10, y), (self.width-10, y)], fill=0, width=1)
    
    def draw_sentence_section(self, draw, sentence_data, y_start):
        """绘制句子部分"""
        font_sentence = ImageFont.truetype(self.config['font_path'], 9)
        font_author = ImageFont.truetype(self.config['font_path'], 8)
        
        y = y_start
        
        # 绘制句子
        sentence = sentence_data.get('sentence', '')
        if sentence:
            lines = self.wrap_text(sentence, self.width - 20, font_sentence)
            for line in lines:
                draw.text((10, y), line, font=font_sentence, fill=0)
                y += 11
        
        # 绘制作者
        author = sentence_data.get('author', '')
        if author:
            author_text = f"— {author}"
            draw.text((self.width - 80, y + 5), author_text, 
                     font=font_author, fill=0)
    
    def wrap_text(self, text, max_width, font):
        """文本换行"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.getsize(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

# 使用自定义主题
theme_config = {
    'width': 250,
    'height': 122,
    'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
}

theme = CustomTheme(theme_config)
image = theme.create_layout(word_data, sentence_data)
```

### 插件系统

创建插件系统来扩展功能：

```python
# src/plugin_manager.py
import importlib
import os
from pathlib import Path

class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir='plugins'):
        self.plugin_dir = Path(plugin_dir)
        self.plugins = {}
        self.hooks = {
            'before_fetch': [],
            'after_fetch': [],
            'before_display': [],
            'after_display': []
        }
    
    def load_plugins(self):
        """加载所有插件"""
        if not self.plugin_dir.exists():
            return
        
        for plugin_file in self.plugin_dir.glob('*.py'):
            if plugin_file.name.startswith('_'):
                continue
            
            plugin_name = plugin_file.stem
            try:
                spec = importlib.util.spec_from_file_location(
                    plugin_name, plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'Plugin'):
                    plugin = module.Plugin()
                    self.plugins[plugin_name] = plugin
                    self.register_hooks(plugin)
                    
            except Exception as e:
                print(f"加载插件 {plugin_name} 失败: {e}")
    
    def register_hooks(self, plugin):
        """注册插件钩子"""
        for hook_name in self.hooks.keys():
            if hasattr(plugin, hook_name):
                self.hooks[hook_name].append(getattr(plugin, hook_name))
    
    def execute_hook(self, hook_name, *args, **kwargs):
        """执行钩子函数"""
        results = []
        for hook_func in self.hooks.get(hook_name, []):
            try:
                result = hook_func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"执行钩子 {hook_name} 失败: {e}")
        return results

# 示例插件
# plugins/weather_plugin.py
class Plugin:
    """天气信息插件"""
    
    def before_display(self, word_data, sentence_data):
        """在显示前添加天气信息"""
        weather_info = self.get_weather()
        if weather_info:
            sentence_data['weather'] = weather_info
        return word_data, sentence_data
    
    def get_weather(self):
        """获取天气信息"""
        # 实现天气API调用
        return "晴天 25°C"
```

## 📊 性能优化

### 缓存策略

```python
# src/cache_manager.py
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir='data/cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache = {}
        self.cache_ttl = 3600  # 1小时
    
    def get(self, key: str, default=None) -> Any:
        """获取缓存数据"""
        # 先检查内存缓存
        if key in self.memory_cache:
            data, timestamp = self.memory_cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
            else:
                del self.memory_cache[key]
        
        # 检查文件缓存
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                if time.time() - cache_data['timestamp'] < self.cache_ttl:
                    # 更新内存缓存
                    self.memory_cache[key] = (cache_data['data'], cache_data['timestamp'])
                    return cache_data['data']
                else:
                    cache_file.unlink()  # 删除过期缓存
            except Exception:
                pass
        
        return default
    
    def set(self, key: str, data: Any) -> bool:
        """设置缓存数据"""
        timestamp = time.time()
        
        # 更新内存缓存
        self.memory_cache[key] = (data, timestamp)
        
        # 更新文件缓存
        cache_file = self.cache_dir / f"{key}.json"
        try:
            cache_data = {
                'data': data,
                'timestamp': timestamp
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            return True
        except Exception:
            return False
    
    def clear(self, key: Optional[str] = None):
        """清理缓存"""
        if key:
            # 清理特定缓存
            self.memory_cache.pop(key, None)
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()
        else:
            # 清理所有缓存
            self.memory_cache.clear()
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
```

### 异步处理

```python
# src/async_manager.py
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

class AsyncAPIManager:
    """异步API管理器"""
    
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_multiple(self, urls):
        """并发获取多个URL"""
        tasks = [self.fetch_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def fetch_single(self, url):
        """获取单个URL"""
        try:
            async with self.session.get(url, timeout=10) as response:
                return await response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def run_sync(self, coro):
        """在同步环境中运行异步代码"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

# 使用示例
async def fetch_all_data():
    urls = [
        'https://api.wordnik.com/v4/words.json/wordOfTheDay',
        'https://api.quotable.io/random'
    ]
    
    async with AsyncAPIManager() as manager:
        results = await manager.fetch_multiple(urls)
        return results

# 在同步代码中使用
manager = AsyncAPIManager()
results = manager.run_sync(fetch_all_data())
```

## 🧪 测试框架

### 单元测试

```python
# tests/test_word_api.py
import unittest
from unittest.mock import patch, MagicMock
from src.class_word_api import WordAPI

class TestWordAPI(unittest.TestCase):
    """WordAPI单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.api = WordAPI()
    
    @patch('requests.get')
    def test_get_word_success(self, mock_get):
        """测试成功获取单词"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'word': 'test',
            'definitions': [{'text': 'test definition'}]
        }
        mock_get.return_value = mock_response
        
        # 执行测试
        result = self.api.get_word_of_day()
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result['word'], 'test')
    
    @patch('requests.get')
    def test_get_word_failure(self, mock_get):
        """测试获取单词失败"""
        # 模拟网络错误
        mock_get.side_effect = Exception("Network error")
        
        # 执行测试
        result = self.api.get_word_of_day()
        
        # 验证结果
        self.assertIsNone(result)
    
    def test_cache_functionality(self):
        """测试缓存功能"""
        test_data = {'word': 'cache_test'}
        
        # 保存到缓存
        success = self.api.save_to_cache(test_data, 'word')
        self.assertTrue(success)
        
        # 从缓存读取
        cached_data = self.api.load_from_cache('word')
        self.assertEqual(cached_data['word'], 'cache_test')

if __name__ == '__main__':
    unittest.main()
```

### 集成测试

```python
# tests/test_integration.py
import unittest
import time
from src.class_word_api import WordAPI
from src.epaper_display_rpi import EPaperDisplay

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.api = WordAPI()
        self.display = EPaperDisplay()
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 获取数据
        success = self.api.get_daily_content()
        self.assertTrue(success)
        
        # 2. 验证数据格式
        self.assertIsNotNone(self.api.word_data)
        self.assertIsNotNone(self.api.sentence_data)
        
        # 3. 显示内容
        display_success = self.display.display_content(
            self.api.word_data, 
            self.api.sentence_data
        )
        self.assertTrue(display_success)
    
    def test_fallback_mechanism(self):
        """测试备用机制"""
        # 模拟网络断开
        original_url = self.api.config['word_api_url']
        self.api.config['word_api_url'] = 'http://invalid-url.com'
        
        # 应该使用本地备用内容
        success = self.api.get_daily_content()
        self.assertTrue(success)
        
        # 恢复原始配置
        self.api.config['word_api_url'] = original_url
```

---

**完成！** API参考文档已创建完成。