#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - 配置文件
Daily Word E-Paper Display System - Configuration

统一配置管理，包含所有系统参数和个性化设置
"""

import os
from pathlib import Path

# ==================== 基础配置 ====================

# 项目信息
PROJECT_NAME = "Daily Word E-Paper Display"
PROJECT_VERSION = "1.0.0"
PROJECT_AUTHOR = "Daily Word Team"

# 路径配置
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
THEMES_DIR = BASE_DIR / "themes"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
THEMES_DIR.mkdir(exist_ok=True)

# ==================== 硬件配置 ====================

# 墨水屏配置
EPAPER_CONFIG = {
    # 支持的墨水屏型号
    'model': 'epd2in13_V4',  # 默认2.13英寸V4版本
    'width': 250,
    'height': 122,
    
    # GPIO引脚配置 (BCM编号)
    'gpio_pins': {
        'RST_PIN': 17,    # 复位引脚
        'DC_PIN': 25,     # 数据/命令引脚
        'CS_PIN': 8,      # 片选引脚
        'BUSY_PIN': 24,   # 忙碌状态引脚
    },
    
    # SPI配置
    'spi_config': {
        'bus': 0,
        'device': 0,
        'max_speed_hz': 4000000,
    },
    
    # 显示配置
    'display_config': {
        'rotation': 0,        # 旋转角度 (0, 90, 180, 270)
        'flip_horizontal': False,
        'flip_vertical': False,
        'partial_update': True,   # 是否支持局部刷新
        'full_update_interval': 10,  # 每N次局部刷新后进行一次全刷新
    }
}

# 支持的墨水屏型号配置
SUPPORTED_EPAPER_MODELS = {
    'epd2in13_V4': {'width': 250, 'height': 122, 'name': '2.13英寸 V4'},
    'epd2in9_V2': {'width': 296, 'height': 128, 'name': '2.9英寸 V2'},
    'epd4in2': {'width': 400, 'height': 300, 'name': '4.2英寸'},
    'epd7in5_V2': {'width': 800, 'height': 480, 'name': '7.5英寸 V2'},
}

# ==================== API配置 ====================

# 单词API配置
WORD_API_CONFIG = {
    'primary': {
        'name': 'Free Dictionary API',
        'base_url': 'https://api.dictionaryapi.dev/api/v2',
        'endpoints': {
            'word_of_day': '/words.json/wordOfTheDay',
            'word_definition': '/word.json/{word}/definitions',
            'word_example': '/word.json/{word}/examples',
        },
        'api_key': None,  # 需要申请API密钥
        'timeout': 10,
        'retry_count': 3,
    },
    
    'fallback': {
        'name': 'Wordnik',
        'base_url': 'https://api.wordnik.com/v4',
        'endpoints': {
            'word_of_day': '/words.json/wordOfTheDay',
            'word_definition': '/word.json/{word}/definitions',
            'word_example': '/word.json/{word}/examples',
        },
        'api_key': None,  # 需要申请API密钥
        'timeout': 10,
        'retry_count': 3,
        'enabled': False,  # 默认禁用，需要API密钥
    },
    
    'secondary_fallback': {
        'name': 'WordsAPI (RapidAPI)',
        'base_url': 'https://wordsapiv1.p.rapidapi.com',
        'endpoints': {
            'word_definition': '/words/{word}',
        },
        'timeout': 15,
        'retry_count': 2,
        'headers': {
            'X-RapidAPI-Host': 'wordsapiv1.p.rapidapi.com',
            'X-RapidAPI-Key': None  # 需要API密钥
        },
        'enabled': False,  # 默认禁用，需要API密钥
    }
}

# 句子API配置
QUOTE_API_CONFIG = {
    'primary': {
        'name': 'Quotable',
        'base_url': 'https://api.quotable.io',
        'endpoints': {
            'random_quote': '/random',
            'quote_by_tag': '/random?tags={tag}',
        },
        'timeout': 10,
        'retry_count': 3,
    },
    
    'fallback': {
        'name': 'ZenQuotes',
        'base_url': 'https://zenquotes.io/api',
        'endpoints': {
            'random_quote': '/random',
            'today_quote': '/today',
        },
        'timeout': 10,
        'retry_count': 2,
    }
}

# ==================== 显示配置 ====================

# 字体配置
FONT_CONFIG = {
    'font_paths': {
        'default': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'bold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        'mono': '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    },
    
    'font_sizes': {
        'title': 16,          # 标题字体大小
        'word': 20,           # 单词字体大小
        'phonetic': 12,       # 音标字体大小
        'definition': 11,     # 定义字体大小
        'example': 10,        # 例句字体大小
        'quote': 11,          # 句子字体大小
        'author': 9,          # 作者字体大小
        'date': 8,            # 日期字体大小
    },
    
    'line_spacing': 2,        # 行间距
    'paragraph_spacing': 4,   # 段落间距
}

# 布局配置
LAYOUT_CONFIG = {
    'margins': {
        'top': 8,
        'bottom': 8,
        'left': 8,
        'right': 8,
    },
    
    'sections': {
        'header_height': 20,      # 标题区域高度
        'word_section_height': 45, # 单词区域高度
        'definition_section_height': 35, # 定义区域高度
        'quote_section_height': 30, # 句子区域高度
        'footer_height': 12,      # 底部区域高度
    },
    
    'separators': {
        'show_lines': True,       # 是否显示分隔线
        'line_thickness': 1,      # 分隔线粗细
        'line_style': 'solid',    # 分隔线样式
    }
}

# 主题配置
THEME_CONFIG = {
    'current_theme': 'modern',  # 当前使用的主题
    
    'themes': {
        'classic': {
            'name': '经典主题',
            'background_color': 255,  # 白色背景
            'text_color': 0,          # 黑色文字
            'accent_color': 128,      # 灰色强调
            'border_style': 'simple',
            'font_style': 'serif',
        },
        
        'modern': {
            'name': '现代主题',
            'background_color': 255,
            'text_color': 0,
            'accent_color': 64,
            'border_style': 'rounded',
            'font_style': 'sans-serif',
        },
        
        'minimal': {
            'name': '极简主题',
            'background_color': 255,
            'text_color': 0,
            'accent_color': 192,
            'border_style': 'none',
            'font_style': 'minimal',
        }
    }
}

# ==================== 更新配置 ====================

# 更新策略配置
UPDATE_CONFIG = {
    'mode': 'interval',  # 更新模式: scheduled, interval, manual - 改为间隔模式
    
    # 定时更新配置
    'scheduled': {
        'update_times': ['08:00', '12:00', '18:00'],  # 每日更新时间
        'timezone': 'Asia/Shanghai',                   # 时区设置
        'random_delay': 300,                          # 随机延迟(秒)，避免同时请求
    },
    
    # 间隔更新配置 - 每10分钟更新
    'interval': {
        'update_interval': 600,   # 更新间隔(秒) - 10分钟
        'min_interval': 300,      # 最小间隔(秒) - 5分钟
        'max_interval': 1800,     # 最大间隔(秒) - 30分钟
    },
    
    # 内容更新策略
    'content_strategy': {
        'word_update_frequency': 'daily',    # 单词更新频率: daily, hourly
        'quote_update_frequency': 'daily',   # 句子更新频率: daily, hourly
        'force_new_content': False,          # 是否强制获取新内容
        'cache_duration': 86400,             # 缓存持续时间(秒)
    }
}

# ==================== 缓存配置 ====================

# 缓存配置
CACHE_CONFIG = {
    'cache_dir': DATA_DIR,
    'cache_files': {
        'word_cache': 'daily_word_cache.json',
        'quote_cache': 'daily_quote_cache.json',
        'favorites': 'daily_word_favorites.json',
        'statistics': 'daily_word_stats.json',
    },
    
    'cache_settings': {
        'max_cache_size': 1000,      # 最大缓存条目数
        'cache_cleanup_interval': 7,  # 缓存清理间隔(天)
        'backup_cache': True,        # 是否备份缓存
        'compress_cache': False,     # 是否压缩缓存文件
    }
}

# ==================== 日志配置 ====================

# 日志配置
LOGGING_CONFIG = {
    'log_level': 'INFO',  # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
    'log_dir': LOGS_DIR,
    'log_files': {
        'main': 'daily_word_main.log',
        'api': 'daily_word_api.log',
        'display': 'daily_word_display.log',
        'error': 'daily_word_error.log',
    },
    
    'log_settings': {
        'max_file_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5,                   # 保留5个备份文件
        'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'date_format': '%Y-%m-%d %H:%M:%S',
        'encoding': 'utf-8',
    }
}

# ==================== 系统配置 ====================

# 系统监控配置
MONITOR_CONFIG = {
    'enable_monitoring': True,
    'monitor_interval': 300,      # 监控间隔(秒)
    'metrics_file': DATA_DIR / 'daily_word_metrics.json',
    
    'monitored_metrics': {
        'cpu_usage': True,
        'memory_usage': True,
        'disk_usage': True,
        'temperature': True,
        'network_status': True,
        'display_status': True,
        'show_ip_address': True,    # 显示IP地址
    },
    
    'alert_thresholds': {
        'cpu_usage': 80,          # CPU使用率阈值(%)
        'memory_usage': 85,       # 内存使用率阈值(%)
        'disk_usage': 90,         # 磁盘使用率阈值(%)
        'temperature': 70,        # 温度阈值(°C)
    }
}

# 服务配置
SERVICE_CONFIG = {
    'service_name': 'daily-word-epaper',
    'service_description': 'Daily Word E-Paper Display Service',
    'service_user': 'pi',
    'working_directory': str(BASE_DIR),
    'restart_policy': 'always',
    'restart_delay': 10,
}

# ==================== 备用内容 ====================

# 备用单词内容
FALLBACK_WORDS = [
    {
        'word': 'serendipity',
        'phonetic': '/ˌserənˈdipədē/',
        'definition': 'The occurrence and development of events by chance in a happy or beneficial way.',
        'example': 'A fortunate stroke of serendipity brought the two old friends together.',
        'date': '2025-01-01'
    },
    {
        'word': 'ephemeral',
        'phonetic': '/əˈfem(ə)rəl/',
        'definition': 'Lasting for a very short time.',
        'example': 'The beauty of cherry blossoms is ephemeral but unforgettable.',
        'date': '2025-01-02'
    },
    {
        'word': 'mellifluous',
        'phonetic': '/məˈliflo͞oəs/',
        'definition': 'Sweet or musical; pleasant to hear.',
        'example': 'Her mellifluous voice captivated the entire audience.',
        'date': '2025-01-03'
    },
    {
        'word': 'ubiquitous',
        'phonetic': '/yo͞oˈbikwədəs/',
        'definition': 'Present, appearing, or found everywhere.',
        'example': 'Smartphones have become ubiquitous in modern society.',
        'date': '2025-01-04'
    },
    {
        'word': 'perspicacious',
        'phonetic': '/ˌpərspəˈkāSHəs/',
        'definition': 'Having a ready insight into and understanding of things.',
        'example': 'The perspicacious detective quickly solved the complex case.',
        'date': '2025-01-05'
    }
]

# 备用句子内容
FALLBACK_QUOTES = [
    {
        'text': 'The only way to do great work is to love what you do.',
        'author': 'Steve Jobs',
        'category': 'motivation',
        'date': '2025-01-01'
    },
    {
        'text': 'Life is what happens to you while you\'re busy making other plans.',
        'author': 'John Lennon',
        'category': 'life',
        'date': '2025-01-02'
    },
    {
        'text': 'The future belongs to those who believe in the beauty of their dreams.',
        'author': 'Eleanor Roosevelt',
        'category': 'dreams',
        'date': '2025-01-03'
    },
    {
        'text': 'It is during our darkest moments that we must focus to see the light.',
        'author': 'Aristotle',
        'category': 'inspiration',
        'date': '2025-01-04'
    },
    {
        'text': 'Success is not final, failure is not fatal: it is the courage to continue that counts.',
        'author': 'Winston Churchill',
        'category': 'success',
        'date': '2025-01-05'
    }
]

# ==================== 功能开关 ====================

# 功能开关配置
FEATURE_FLAGS = {
    'enable_word_display': True,      # 启用单词显示
    'enable_quote_display': True,     # 启用句子显示
    'enable_statistics': True,        # 启用学习统计
    'enable_favorites': True,         # 启用收藏功能
    'enable_themes': True,            # 启用主题切换
    'enable_monitoring': True,        # 启用系统监控
    'enable_auto_update': True,       # 启用自动更新
    'enable_backup': True,            # 启用自动备份
    'enable_web_interface': False,    # 启用Web界面(未来功能)
    'enable_voice_output': False,     # 启用语音输出(未来功能)
}

# ==================== 开发配置 ====================

# 开发和调试配置
DEBUG_CONFIG = {
    'debug_mode': False,              # 调试模式
    'test_mode': False,               # 测试模式
    'mock_hardware': False,           # 模拟硬件(用于开发)
    'mock_api': False,                # 模拟API(用于测试)
    'verbose_logging': False,         # 详细日志
    'performance_profiling': False,   # 性能分析
}

# 测试配置
TEST_CONFIG = {
    'test_data_dir': BASE_DIR / 'tests' / 'data',
    'test_word': {
        'word': 'test',
        'phonetic': '/test/',
        'definition': 'A test word for system testing.',
        'example': 'This is a test example.',
    },
    'test_quote': {
        'text': 'This is a test quote for system testing.',
        'author': 'Test Author',
        'category': 'test',
    }
}

# ==================== 配置验证 ====================

def validate_config():
    """验证配置文件的有效性"""
    errors = []
    
    # 验证必要目录
    required_dirs = [DATA_DIR, LOGS_DIR]
    for dir_path in required_dirs:
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"无法创建目录 {dir_path}: {e}")
    
    # 验证墨水屏配置
    try:
        model = EPAPER_CONFIG['model']
        if model not in SUPPORTED_EPAPER_MODELS:
            errors.append(f"不支持的墨水屏型号: {model}")
    except KeyError:
        errors.append("墨水屏配置缺少model字段")
    
    # 验证主题配置
    try:
        current_theme = THEME_CONFIG['current_theme']
        themes = THEME_CONFIG['themes']
        if current_theme not in themes:
            errors.append(f"不存在的主题: {current_theme}")
    except KeyError as e:
        errors.append(f"主题配置缺少字段: {e}")
    
    # 验证更新时间格式
    try:
        update_times = UPDATE_CONFIG['scheduled']['update_times']
        for time_str in update_times:
            try:
                hour, minute = map(int, time_str.split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    errors.append(f"无效的时间格式: {time_str}")
            except (ValueError, AttributeError):
                errors.append(f"无效的时间格式: {time_str}")
    except KeyError as e:
        errors.append(f"更新配置缺少字段: {e}")
    
    return errors

def get_config_summary():
    """获取配置摘要信息"""
    return {
        'project': f"{PROJECT_NAME} v{PROJECT_VERSION}",
        'epaper_model': EPAPER_CONFIG['model'],
        'current_theme': THEME_CONFIG['current_theme'],
        'update_mode': UPDATE_CONFIG['mode'],
        'log_level': LOGGING_CONFIG['log_level'],
        'features_enabled': sum(1 for v in FEATURE_FLAGS.values() if v),
        'debug_mode': DEBUG_CONFIG['debug_mode'],
    }

# 配置文件加载时自动验证
if __name__ == "__main__":
    errors = validate_config()
    if errors:
        print("配置验证失败:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("配置验证通过")
        print("配置摘要:", get_config_summary())