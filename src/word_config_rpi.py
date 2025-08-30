#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
树莓派4专用配置文件
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# API配置
WORD_API_CONFIG = {
    # 每日单词API
    'word_api_url': 'https://api.wordnik.com/v4/words.json/wordOfTheDay',
    
    # 每日句子API (使用国内可访问的API)
    'sentence_api_url': 'https://v1.hitokoto.cn/?c=i&encode=json',  # 一言API
    
    # 备用句子API
    'backup_sentence_api': 'https://api.quotable.io/random',
    
    # 请求超时时间（秒）
    'timeout': 15,
    
    # 重试次数
    'max_retries': 3,
    
    # 重试间隔（秒）
    'retry_interval': 30
}

# 树莓派墨水屏配置
DISPLAY_CONFIG = {
    # 墨水屏类型 ('waveshare_2in7', 'waveshare_4in2', 'luma_epd')
    'epd_type': 'waveshare_2in7',
    
    # 墨水屏尺寸
    'width': 264,
    'height': 176,
    
    # SPI配置
    'spi_device': 0,
    'spi_bus': 0,
    
    # GPIO引脚配置 (BCM编号)
    'gpio_pins': {
        'rst': 17,
        'dc': 25,
        'cs': 8,
        'busy': 24
    },
    
    # 字体配置
    'fonts': {
        'default': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'bold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        'mono': '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
    },
    
    'font_sizes': {
        'title': 14,
        'word': 16,
        'definition': 10,
        'example': 9,
        'quote': 11,
        'author': 9,
        'date': 8
    },
    
    # 布局配置
    'margins': {
        'top': 5,
        'bottom': 5,
        'left': 5,
        'right': 5
    },
    
    'spacing': {
        'line': 2,
        'paragraph': 8,
        'section': 12
    },
    
    # 显示配置
    'max_line_length': 35,
    'word_wrap': True,
    
    # 颜色配置（0=黑色，255=白色）
    'colors': {
        'background': 255,
        'text': 0,
        'accent': 0
    }
}

# 数据存储配置
DATA_CONFIG = {
    # 数据目录
    'data_dir': PROJECT_ROOT / 'data',
    
    # 文件名
    'word_file': 'daily_word.json',
    'sentence_file': 'daily_sentence.json',
    'log_file': 'daily_word.log',
    'pid_file': 'daily_word.pid',
    
    # 日志配置
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(levelname)s - %(message)s',
    'log_max_size': 10 * 1024 * 1024,  # 10MB
    'log_backup_count': 5
}

# 系统配置
SYSTEM_CONFIG = {
    # 运行模式
    'debug_mode': False,
    
    # 网络检查
    'check_internet': True,
    'internet_check_url': 'https://www.baidu.com',
    'internet_timeout': 5,
    
    # 定时任务
    'update_times': ['08:00', '12:00', '18:00'],  # 每日更新时间
    
    # 系统监控
    'monitor_temperature': True,
    'max_temperature': 70,  # 摄氏度
    
    # 电源管理
    'low_power_mode': False,
    'sleep_between_updates': True
}

# 备用单词列表（网络不可用时使用）
BACKUP_WORDS = [
    {
        "word": "serendipity",
        "definition": "The occurrence and development of events by chance in a happy way",
        "pronunciation": "/ˌserənˈdipədē/",
        "example": "A fortunate stroke of serendipity brought them together.",
        "difficulty": "advanced"
    },
    {
        "word": "resilience",
        "definition": "The ability to recover quickly from difficulties",
        "pronunciation": "/rɪˈzɪljəns/",
        "example": "Her resilience helped her overcome many challenges.",
        "difficulty": "intermediate"
    },
    {
        "word": "innovation",
        "definition": "The action or process of innovating",
        "pronunciation": "/ˌɪnəˈveɪʃən/",
        "example": "The company is known for its innovation in technology.",
        "difficulty": "intermediate"
    },
    {
        "word": "perseverance",
        "definition": "Persistence in doing something despite difficulty",
        "pronunciation": "/ˌpɜːrsəˈvɪrəns/",
        "example": "Success requires perseverance and hard work.",
        "difficulty": "intermediate"
    },
    {
        "word": "eloquent",
        "definition": "Fluent or persuasive in speaking or writing",
        "pronunciation": "/ˈeləkwənt/",
        "example": "She gave an eloquent speech at the graduation ceremony.",
        "difficulty": "advanced"
    }
]

# 备用励志句子列表
BACKUP_QUOTES = [
    {
        "sentence": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs",
        "tags": ["motivation", "work"],
        "language": "en"
    },
    {
        "sentence": "Innovation distinguishes between a leader and a follower.",
        "author": "Steve Jobs",
        "tags": ["innovation", "leadership"],
        "language": "en"
    },
    {
        "sentence": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "author": "Winston Churchill",
        "tags": ["success", "courage"],
        "language": "en"
    },
    {
        "sentence": "The future belongs to those who believe in the beauty of their dreams.",
        "author": "Eleanor Roosevelt",
        "tags": ["dreams", "future"],
        "language": "en"
    },
    {
        "sentence": "千里之行，始于足下。",
        "author": "老子",
        "tags": ["journey", "beginning"],
        "language": "zh"
    }
]

# 环境检查函数
def check_environment():
    """检查树莓派运行环境"""
    issues = []
    
    # 检查是否在树莓派上运行
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'BCM' not in f.read():
                issues.append("Warning: Not running on Raspberry Pi")
    except:
        issues.append("Warning: Cannot detect hardware platform")
    
    # 检查SPI是否启用
    if not os.path.exists('/dev/spidev0.0'):
        issues.append("Error: SPI not enabled. Run 'sudo raspi-config' to enable SPI")
    
    # 检查字体文件
    for font_path in DISPLAY_CONFIG['fonts'].values():
        if not os.path.exists(font_path):
            issues.append(f"Warning: Font file not found: {font_path}")
    
    # 检查数据目录
    data_dir = DATA_CONFIG['data_dir']
    if not data_dir.exists():
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Error: Cannot create data directory: {e}")
    
    return issues

# 获取系统信息
def get_system_info():
    """获取系统信息"""
    info = {}
    
    try:
        # CPU温度
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read()) / 1000.0
            info['cpu_temperature'] = temp
    except:
        info['cpu_temperature'] = None
    
    try:
        # 内存使用
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('MemAvailable:'):
                    info['memory_available'] = int(line.split()[1]) * 1024
                    break
    except:
        info['memory_available'] = None
    
    try:
        # 磁盘空间
        import shutil
        total, used, free = shutil.disk_usage('/')
        info['disk_free'] = free
    except:
        info['disk_free'] = None
    
    return info