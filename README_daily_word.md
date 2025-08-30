# 每日单词墨水屏显示系统

这是一个基于树莓派和墨水屏的每日单词和励志句子显示系统，参照原有的诗词API代码结构开发。

## 功能特性

- 📚 **每日单词**: 获取英语单词及其定义、发音、例句
- 💭 **励志句子**: 获取每日励志名言和格言
- 🖥️ **墨水屏显示**: 适配墨水屏的显示格式和布局
- 💾 **本地缓存**: 自动保存内容到本地文件，离线可用
- 🔄 **自动重试**: 网络失败时自动重试机制
- 📝 **日志记录**: 详细的运行日志便于调试

## 文件结构

```
src/
├── class_word_api.py      # 核心API类
├── daily_word_display.py  # 墨水屏显示控制器
├── word_config.py         # 配置文件
├── test_word_api.py       # 测试脚本
└── class_poem_api.py      # 原有诗词API（参考）

data/
├── daily_word.json        # 单词数据缓存
├── daily_sentence.json    # 句子数据缓存
└── daily_word.log         # 运行日志
```

## 安装依赖

```bash
pip install requests pathlib
```

如果需要在实际墨水屏上显示，还需要安装相应的墨水屏库：

```bash
# 例如，对于Waveshare墨水屏
pip install waveshare-epd
```

## 使用方法

### 1. 测试功能

```bash
cd src
python test_word_api.py
```

### 2. 运行显示程序

```bash
# 正常运行
python daily_word_display.py

# 测试模式（仅在控制台显示）
python daily_word_display.py --test
```

### 3. 定时任务

可以使用crontab设置每日自动更新：

```bash
# 编辑crontab
crontab -e

# 添加每日8点更新的任务
0 8 * * * cd /path/to/your/project/src && python daily_word_display.py
```

## 配置说明

在 `word_config.py` 中可以配置：

- **API地址**: 更换不同的单词和句子API
- **显示参数**: 墨水屏尺寸、字体、布局等
- **备用内容**: 当API不可用时使用的本地内容
- **重试设置**: 网络请求的重试次数和间隔

## API接口

### WordAPI类主要方法

```python
from class_word_api import WordAPI

# 创建实例
word_api = WordAPI()

# 获取每日内容
success = word_api.get_daily_content()

# 获取格式化显示内容
content = word_api.format_display_content()

# 获取内容摘要
summary = word_api.get_summary()
```

### 数据结构

单词数据：
```json
{
  "word": "serendipity",
  "definition": "The occurrence and development of events by chance...",
  "pronunciation": "/ˌserənˈdipədē/",
  "example": "A fortunate stroke of serendipity...",
  "date": "2024-01-01"
}
```

句子数据：
```json
{
  "sentence": "The only way to do great work is to love what you do.",
  "author": "Steve Jobs",
  "tags": ["motivation", "work", "passion"],
  "date": "2024-01-01"
}
```

## 墨水屏适配

代码已经为墨水屏显示进行了优化：

- **自动换行**: 根据屏幕宽度自动换行
- **合适字体**: 使用适合墨水屏的字体大小
- **清晰布局**: 合理的间距和分隔线
- **黑白显示**: 适配墨水屏的黑白显示特性

## 扩展功能

可以根据需要添加以下功能：

1. **多语言支持**: 添加中文单词或其他语言
2. **主题切换**: 不同的显示主题和布局
3. **历史记录**: 保存和查看历史内容
4. **用户自定义**: 允许用户添加自定义单词和句子
5. **统计功能**: 学习进度和统计信息

## 故障排除

### 常见问题

1. **网络连接失败**: 检查网络连接，程序会自动使用本地缓存
2. **墨水屏不显示**: 检查硬件连接和驱动库安装
3. **字体显示异常**: 确认字体文件路径正确
4. **权限问题**: 确保程序有读写data目录的权限

### 日志查看

```bash
tail -f data/daily_word.log
```

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License