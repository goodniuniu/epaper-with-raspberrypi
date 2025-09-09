#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
每日单词配置文件
"""

# API配置
WORD_API_CONFIG = {
    # 每日单词API（可以替换为其他API）
    'word_api_url': 'https://api.wordnik.com/v4/words.json/wordOfTheDay',
    
    # 每日句子API
    'sentence_api_url': 'https://api.quotable.io/random',
    
    # 请求超时时间（秒）
    'timeout': 10,
    
    # 重试次数
    'max_retries': 3,
    
    # 重试间隔（秒）
    'retry_interval': 30
}

# 显示配置
DISPLAY_CONFIG = {
    # 墨水屏尺寸
    'width': 400,
    'height': 300,
    
    # 字体配置
    'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    'font_size': 12,
    'title_font_size': 16,
    
    # 布局配置
    'margin': 10,
    'line_spacing': 15,
    'max_line_length': 35,
    
    # 颜色配置（0=黑色，255=白色）
    'background_color': 255,
    'text_color': 0
}

# 数据存储配置
DATA_CONFIG = {
    # 数据目录
    'data_dir': 'data',
    
    # 文件名
    'word_file': 'daily_word.json',
    'sentence_file': 'daily_sentence.json',
    'log_file': 'daily_word.log'
}

# 备用单词列表（当API不可用时使用）
BACKUP_WORDS = [
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
    },
    {
        "word": "quintessential",
        "definition": "Representing the most perfect example of a quality or class",
        "pronunciation": "/ˌkwin(t)əˈsen(t)SHəl/",
        "example": "She was the quintessential professional, always prepared and courteous."
    },
    {
        "word": "surreptitious",
        "definition": "Kept secret, especially because it would not be approved of",
        "pronunciation": "/ˌsərəpˈtiSHəs/",
        "example": "He cast a surreptitious glance at his watch during the meeting."
    },
    {
        "word": "magnanimous",
        "definition": "Very generous or forgiving, especially toward a rival or less powerful person",
        "pronunciation": "/maɡˈnanəməs/",
        "example": "The champion was magnanimous in victory, praising his opponent's skill."
    }
]

# 备用励志句子列表
BACKUP_QUOTES = [
    {
        "sentence": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs",
        "tags": ["motivation", "work", "passion"]
    },
    {
        "sentence": "Innovation distinguishes between a leader and a follower.",
        "author": "Steve Jobs",
        "tags": ["innovation", "leadership"]
    },
    {
        "sentence": "The future belongs to those who believe in the beauty of their dreams.",
        "author": "Eleanor Roosevelt",
        "tags": ["dreams", "future", "belief"]
    },
    {
        "sentence": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "author": "Winston Churchill",
        "tags": ["success", "failure", "courage"]
    },
    {
        "sentence": "The only impossible journey is the one you never begin.",
        "author": "Tony Robbins",
        "tags": ["journey", "beginning", "possibility"]
    }
]