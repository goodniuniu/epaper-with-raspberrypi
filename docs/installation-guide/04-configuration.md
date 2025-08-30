# 系统参数配置

## 📋 概述

本章节将指导您配置每日单词墨水屏显示系统的各项参数，包括硬件配置、API设置、显示参数和系统选项。

## 📁 配置文件结构

```
src/
├── word_config_rpi.py          # 树莓派专用配置（模板）
├── word_config.py              # 实际使用的配置文件
└── config/
    ├── display_profiles/       # 显示配置预设
    ├── api_profiles/          # API配置预设
    └── system_profiles/       # 系统配置预设
```

## 🔧 基础配置

### 创建配置文件

```bash
# 进入项目目录
cd ~/daily-word-epaper

# 复制配置模板
cp src/word_config_rpi.py src/word_config.py

# 编辑配置文件
nano src/word_config.py
```

### 主要配置项

#### 1. 墨水屏配置

```python
DISPLAY_CONFIG = {
    # 墨水屏类型
    'epd_type': 'waveshare_2in7',  # 选项: waveshare_2in7, waveshare_4in2, luma_epd
    
    # 屏幕尺寸
    'width': 264,
    'height': 176,
    
    # GPIO引脚配置 (BCM编号)
    'gpio_pins': {
        'rst': 17,    # 复位引脚
        'dc': 25,     # 数据/命令引脚
        'cs': 8,      # 片选引脚
        'busy': 24    # 忙状态引脚
    },
    
    # 字体配置
    'fonts': {
        'default': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'bold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        'mono': '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
    },
    
    # 字体大小
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
    }
}
```

#### 2. API配置

```python
WORD_API_CONFIG = {
    # 每日单词API
    'word_api_url': 'https://api.wordnik.com/v4/words.json/wordOfTheDay',
    
    # 每日句子API
    'sentence_api_url': 'https://v1.hitokoto.cn/?c=i&encode=json',
    
    # 备用API
    'backup_sentence_api': 'https://api.quotable.io/random',
    
    # 请求配置
    'timeout': 15,
    'max_retries': 3,
    'retry_interval': 30
}
```

#### 3. 系统配置

```python
SYSTEM_CONFIG = {
    # 运行模式
    'debug_mode': False,
    
    # 网络检查
    'check_internet': True,
    'internet_check_url': 'https://www.baidu.com',
    'internet_timeout': 5,
    
    # 定时任务
    'update_times': ['08:00', '12:00', '18:00'],
    
    # 系统监控
    'monitor_temperature': True,
    'max_temperature': 70,  # 摄氏度
    
    # 电源管理
    'low_power_mode': False,
    'sleep_between_updates': True
}
```

## 🖥️ 硬件配置详解

### 支持的墨水屏型号

| 型号 | epd_type值 | 分辨率 | 配置示例 |
|------|------------|--------|----------|
| Waveshare 2.7" | `waveshare_2in7` | 264×176 | [查看配置](#waveshare-27寸配置) |
| Waveshare 4.2" | `waveshare_4in2` | 400×300 | [查看配置](#waveshare-42寸配置) |
| 通用EPD | `luma_epd` | 自定义 | [查看配置](#通用epd配置) |

### Waveshare 2.7寸配置

```python
DISPLAY_CONFIG = {
    'epd_type': 'waveshare_2in7',
    'width': 264,
    'height': 176,
    'gpio_pins': {
        'rst': 17,
        'dc': 25,
        'cs': 8,
        'busy': 24
    },
    'font_sizes': {
        'title': 12,
        'word': 14,
        'definition': 9,
        'example': 8,
        'quote': 10,
        'author': 8,
        'date': 7
    }
}
```

### Waveshare 4.2寸配置

```python
DISPLAY_CONFIG = {
    'epd_type': 'waveshare_4in2',
    'width': 400,
    'height': 300,
    'gpio_pins': {
        'rst': 17,
        'dc': 25,
        'cs': 8,
        'busy': 24
    },
    'font_sizes': {
        'title': 16,
        'word': 20,
        'definition': 12,
        'example': 11,
        'quote': 14,
        'author': 11,
        'date': 10
    }
}
```

### 通用EPD配置

```python
DISPLAY_CONFIG = {
    'epd_type': 'luma_epd',
    'width': 264,  # 根据实际屏幕调整
    'height': 176,
    'spi_device': 0,
    'spi_bus': 0,
    'gpio_pins': {
        'rst': 17,
        'dc': 25,
        'cs': 8,
        'busy': 24
    }
}
```

## 🌐 API配置详解

### 支持的API服务

#### 单词API选项

| 服务 | URL | 特点 | 配置示例 |
|------|-----|------|----------|
| Wordnik | `api.wordnik.com` | 英文单词，需要API Key | [查看配置](#wordnik-api) |
| 本地词库 | 内置 | 离线可用 | [查看配置](#本地词库) |

#### 句子API选项

| 服务 | URL | 特点 | 配置示例 |
|------|-----|------|----------|
| 一言 | `v1.hitokoto.cn` | 中文句子，免费 | [查看配置](#一言api) |
| Quotable | `api.quotable.io` | 英文名言，免费 | [查看配置](#quotable-api) |

### Wordnik API

```python
WORD_API_CONFIG = {
    'word_api_url': 'https://api.wordnik.com/v4/words.json/wordOfTheDay',
    'api_key': 'your_api_key_here',  # 需要注册获取
    'timeout': 15
}
```

### 一言API

```python
WORD_API_CONFIG = {
    'sentence_api_url': 'https://v1.hitokoto.cn/?c=i&encode=json',
    'sentence_params': {
        'c': 'i',  # 诗词类型
        'encode': 'json'
    }
}
```

### Quotable API

```python
WORD_API_CONFIG = {
    'sentence_api_url': 'https://api.quotable.io/random',
    'sentence_params': {
        'minLength': 50,
        'maxLength': 150,
        'tags': 'motivational'
    }
}
```

## 🎨 显示配置详解

### 字体配置

#### 系统字体路径

```python
# 英文字体
FONTS = {
    'dejavu_sans': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    'dejavu_bold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    'dejavu_mono': '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
}

# 中文字体（需要安装）
CHINESE_FONTS = {
    'wqy_zenhei': '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    'wqy_microhei': '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
}
```

#### 字体大小建议

| 屏幕尺寸 | 标题 | 单词 | 定义 | 例句 | 句子 | 作者 | 日期 |
|----------|------|------|------|------|------|------|------|
| 2.7寸 | 12 | 14 | 9 | 8 | 10 | 8 | 7 |
| 4.2寸 | 16 | 20 | 12 | 11 | 14 | 11 | 10 |

### 布局配置

#### 边距设置

```python
# 紧凑布局（适合小屏幕）
'margins': {
    'top': 3,
    'bottom': 3,
    'left': 3,
    'right': 3
}

# 标准布局
'margins': {
    'top': 5,
    'bottom': 5,
    'left': 5,
    'right': 5
}

# 宽松布局（适合大屏幕）
'margins': {
    'top': 8,
    'bottom': 8,
    'left': 8,
    'right': 8
}
```

#### 间距设置

```python
# 紧凑间距
'spacing': {
    'line': 1,
    'paragraph': 5,
    'section': 8
}

# 标准间距
'spacing': {
    'line': 2,
    'paragraph': 8,
    'section': 12
}

# 宽松间距
'spacing': {
    'line': 3,
    'paragraph': 12,
    'section': 16
}
```

## ⚙️ 高级配置

### 性能优化配置

```python
PERFORMANCE_CONFIG = {
    # 缓存设置
    'enable_cache': True,
    'cache_duration': 3600,  # 秒
    
    # 图像优化
    'image_quality': 'high',  # low, medium, high
    'dithering': True,
    
    # 网络优化
    'connection_pool_size': 5,
    'keep_alive': True,
    
    # 内存管理
    'max_memory_usage': 100,  # MB
    'garbage_collection': True
}
```

### 日志配置

```python
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'data/daily_word.log',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'console_output': True
}
```

### 安全配置

```python
SECURITY_CONFIG = {
    # API安全
    'verify_ssl': True,
    'user_agent': 'DailyWordDisplay/1.0',
    
    # 文件权限
    'file_permissions': 0o644,
    'dir_permissions': 0o755,
    
    # 网络安全
    'allowed_hosts': [
        'api.wordnik.com',
        'v1.hitokoto.cn',
        'api.quotable.io'
    ]
}
```

## 🔧 配置工具

### 配置生成器

创建配置生成脚本：

```bash
cat > scripts/generate_config.py << 'EOF'
#!/usr/bin/env python3
"""
配置文件生成器
根据用户输入生成适合的配置文件
"""

import json
from pathlib import Path

def get_epaper_config():
    """获取墨水屏配置"""
    print("请选择墨水屏型号:")
    print("1) Waveshare 2.7寸")
    print("2) Waveshare 4.2寸")
    print("3) 其他/自定义")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == '1':
        return {
            'epd_type': 'waveshare_2in7',
            'width': 264,
            'height': 176,
            'font_sizes': {
                'title': 12, 'word': 14, 'definition': 9,
                'example': 8, 'quote': 10, 'author': 8, 'date': 7
            }
        }
    elif choice == '2':
        return {
            'epd_type': 'waveshare_4in2',
            'width': 400,
            'height': 300,
            'font_sizes': {
                'title': 16, 'word': 20, 'definition': 12,
                'example': 11, 'quote': 14, 'author': 11, 'date': 10
            }
        }
    else:
        width = int(input("屏幕宽度: "))
        height = int(input("屏幕高度: "))
        return {
            'epd_type': 'custom',
            'width': width,
            'height': height,
            'font_sizes': {
                'title': 14, 'word': 16, 'definition': 10,
                'example': 9, 'quote': 11, 'author': 9, 'date': 8
            }
        }

def get_api_config():
    """获取API配置"""
    print("\n请选择句子API:")
    print("1) 一言 (中文句子)")
    print("2) Quotable (英文名言)")
    print("3) 自定义")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == '1':
        return {
            'sentence_api_url': 'https://v1.hitokoto.cn/?c=i&encode=json'
        }
    elif choice == '2':
        return {
            'sentence_api_url': 'https://api.quotable.io/random'
        }
    else:
        url = input("API URL: ")
        return {
            'sentence_api_url': url
        }

def generate_config():
    """生成配置文件"""
    print("=== 配置文件生成器 ===\n")
    
    epaper_config = get_epaper_config()
    api_config = get_api_config()
    
    config = {
        'DISPLAY_CONFIG': {
            **epaper_config,
            'gpio_pins': {
                'rst': 17,
                'dc': 25,
                'cs': 8,
                'busy': 24
            },
            'margins': {'top': 5, 'bottom': 5, 'left': 5, 'right': 5},
            'spacing': {'line': 2, 'paragraph': 8, 'section': 12}
        },
        'WORD_API_CONFIG': {
            **api_config,
            'timeout': 15,
            'max_retries': 3
        },
        'SYSTEM_CONFIG': {
            'debug_mode': False,
            'update_times': ['08:00', '12:00', '18:00']
        }
    }
    
    # 保存配置文件
    config_file = Path('src/word_config.py')
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write("# 自动生成的配置文件\n\n")
        for key, value in config.items():
            f.write(f"{key} = {repr(value)}\n\n")
    
    print(f"\n✅ 配置文件已生成: {config_file}")
    print("请根据需要进一步调整配置参数")

if __name__ == "__main__":
    generate_config()
EOF

chmod +x scripts/generate_config.py
```

### 配置验证器

```bash
cat > scripts/validate_config.py << 'EOF'
#!/usr/bin/env python3
"""
配置文件验证器
检查配置文件的正确性
"""

import sys
from pathlib import Path

def validate_display_config(config):
    """验证显示配置"""
    errors = []
    
    required_keys = ['epd_type', 'width', 'height', 'gpio_pins']
    for key in required_keys:
        if key not in config:
            errors.append(f"缺少必需的显示配置项: {key}")
    
    if 'gpio_pins' in config:
        required_pins = ['rst', 'dc', 'cs', 'busy']
        for pin in required_pins:
            if pin not in config['gpio_pins']:
                errors.append(f"缺少GPIO引脚配置: {pin}")
    
    return errors

def validate_api_config(config):
    """验证API配置"""
    errors = []
    
    if 'sentence_api_url' not in config:
        errors.append("缺少句子API配置")
    
    if 'timeout' in config and config['timeout'] <= 0:
        errors.append("超时时间必须大于0")
    
    return errors

def validate_config_file(config_path):
    """验证配置文件"""
    if not config_path.exists():
        return [f"配置文件不存在: {config_path}"]
    
    try:
        # 导入配置模块
        sys.path.insert(0, str(config_path.parent))
        config_module = __import__(config_path.stem)
        
        errors = []
        
        # 验证显示配置
        if hasattr(config_module, 'DISPLAY_CONFIG'):
            errors.extend(validate_display_config(config_module.DISPLAY_CONFIG))
        else:
            errors.append("缺少DISPLAY_CONFIG配置")
        
        # 验证API配置
        if hasattr(config_module, 'WORD_API_CONFIG'):
            errors.extend(validate_api_config(config_module.WORD_API_CONFIG))
        else:
            errors.append("缺少WORD_API_CONFIG配置")
        
        return errors
        
    except Exception as e:
        return [f"配置文件语法错误: {e}"]

if __name__ == "__main__":
    config_path = Path('src/word_config.py')
    errors = validate_config_file(config_path)
    
    if errors:
        print("❌ 配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ 配置验证通过")
EOF

chmod +x scripts/validate_config.py
```

## 📋 配置检查清单

完成配置后，请确认以下项目：

- [ ] 墨水屏型号配置正确
- [ ] GPIO引脚配置匹配硬件连接
- [ ] 字体文件路径存在
- [ ] 字体大小适合屏幕尺寸
- [ ] API URL可访问
- [ ] 网络超时设置合理
- [ ] 更新时间设置合适
- [ ] 日志配置正确
- [ ] 配置文件语法正确

## 🔍 配置测试

### 运行配置测试

```bash
# 验证配置文件
python3 scripts/validate_config.py

# 测试显示配置
python3 -c "
from src.word_config import DISPLAY_CONFIG
print('显示配置:', DISPLAY_CONFIG)
"

# 测试API配置
python3 -c "
from src.word_config import WORD_API_CONFIG
import requests
try:
    response = requests.get(WORD_API_CONFIG['sentence_api_url'], timeout=5)
    print('✅ API连接正常')
except Exception as e:
    print('❌ API连接失败:', e)
"
```

---

**下一步：** [部署和运行](05-deployment.md)