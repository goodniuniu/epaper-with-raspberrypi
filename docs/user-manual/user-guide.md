# 用户使用手册

## 📋 概述

欢迎使用每日单词墨水屏显示系统！本手册将指导您如何使用系统的各项功能，包括日常操作、个性化设置和维护管理。

## 🚀 快速开始

### 首次使用

系统安装完成后，您可以通过以下步骤开始使用：

#### 1. 验证系统状态

```bash
# 检查服务状态
./manage.sh status

# 预期输出：
# ✅ daily-word服务: 运行中
# ✅ 墨水屏连接: 正常
# ✅ 网络连接: 正常
```

#### 2. 手动更新显示

```bash
# 立即更新显示内容
./manage.sh update

# 预期看到墨水屏显示新的单词和句子
```

#### 3. 查看当前内容

```bash
# 查看最近的日志
./manage.sh logs

# 或查看详细状态
python3 scripts/dashboard.py
```

### 基本操作命令

系统提供了便捷的管理脚本，所有操作都可以通过 `manage.sh` 完成：

```bash
# 查看所有可用命令
./manage.sh help

# 常用命令：
./manage.sh start      # 启动服务
./manage.sh stop       # 停止服务
./manage.sh restart    # 重启服务
./manage.sh status     # 查看状态
./manage.sh update     # 手动更新
./manage.sh clear      # 清空显示
./manage.sh test       # 运行测试
./manage.sh logs       # 查看日志
```

## ⚙️ 个性化设置

### 显示内容定制

#### 修改更新时间

编辑配置文件来自定义更新时间：

```bash
# 编辑配置文件
nano src/word_config.py

# 修改更新时间设置
UPDATE_CONFIG = {
    'update_times': ['07:00', '12:00', '17:00', '21:00'],  # 自定义时间
    'update_interval': 3600,    # 更新间隔（秒）
}

# 重启服务使配置生效
./manage.sh restart
```

#### 调整显示样式

```python
# 在 word_config.py 中修改字体和布局
FONT_CONFIG = {
    'font_size_word': 22,       # 增大单词字体
    'font_size_definition': 14, # 增大定义字体
    'line_spacing': 3           # 增加行间距
}

LAYOUT_CONFIG = {
    'margin_top': 8,           # 增加上边距
    'section_spacing': 10,     # 增加段落间距
}
```

#### 选择内容类型

```python
# 配置内容偏好
CONTENT_CONFIG = {
    'word_difficulty': 'intermediate',  # 单词难度: basic/intermediate/advanced
    'sentence_category': 'motivation',  # 句子类别: motivation/wisdom/success
    'max_word_length': 12,             # 最大单词长度
    'max_sentence_length': 100         # 最大句子长度
}
```

### 主题和外观

#### 创建自定义主题

```bash
# 创建主题目录
mkdir -p themes/my_theme

# 创建主题配置文件
cat > themes/my_theme/theme.py << 'EOF'
# 自定义主题配置
THEME_CONFIG = {
    'name': 'My Custom Theme',
    'background_color': 255,    # 白色背景
    'text_color': 0,           # 黑色文字
    'accent_color': 0,         # 强调色
    'border_style': 'simple',  # 边框样式
    'layout_style': 'modern'   # 布局样式
}

# 自定义布局函数
def create_custom_layout(word_data, sentence_data, config):
    # 实现自定义布局逻辑
    pass
EOF

# 应用主题
echo "CURRENT_THEME = 'my_theme'" >> src/word_config.py
./manage.sh restart
```

#### 预设主题

系统提供多个预设主题：

```python
# 在 word_config.py 中选择主题
CURRENT_THEME = 'classic'    # 经典主题
# CURRENT_THEME = 'modern'   # 现代主题
# CURRENT_THEME = 'minimal'  # 极简主题
# CURRENT_THEME = 'elegant'  # 优雅主题
```

### 语言和本地化

#### 设置显示语言

```python
# 配置语言设置
LANGUAGE_CONFIG = {
    'display_language': 'zh-CN',    # 界面语言
    'word_language': 'en',          # 单词语言
    'phonetic_style': 'IPA',        # 音标样式: IPA/US/UK
    'date_format': '%Y年%m月%d日'    # 日期格式
}
```

#### 添加中文支持

```bash
# 安装中文字体
sudo apt install fonts-noto-cjk

# 修改字体配置
nano src/word_config.py

# 更新字体路径
FONT_CONFIG = {
    'font_path': '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    'fallback_font': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
}
```

## 📱 日常使用

### 查看系统状态

#### 使用监控仪表板

```bash
# 查看实时状态
python3 scripts/dashboard.py

# 持续监控模式（每30秒更新）
python3 scripts/dashboard.py --continuous

# 输出示例：
# ==========================================
# 📊 每日单词系统监控仪表板
# ==========================================
# 
# 🖥️ 系统状态:
#   CPU使用率:   15.2%
#   内存使用率:  45.8%
#   磁盘使用率:  23.1%
#   CPU温度:     52.3°C
# 
# 🔧 服务状态:
#   daily-word服务: ✅ 运行中
```

#### 检查显示内容

```bash
# 查看当前显示的内容
cat data/current_display.json

# 查看内容历史
ls -la data/word_cache.json data/sentence_cache.json

# 查看最近更新时间
stat data/daily_word.log | grep Modify
```

### 手动操作

#### 立即更新内容

```bash
# 强制更新显示内容
./manage.sh update

# 使用特定模式更新
python3 src/daily_word_rpi.py --mode once

# 测试模式（不实际显示）
python3 src/daily_word_rpi.py --test
```

#### 清空显示

```bash
# 清空墨水屏显示
./manage.sh clear

# 或直接调用
python3 src/daily_word_rpi.py --clear
```

#### 重启系统

```bash
# 重启服务
./manage.sh restart

# 重启整个系统（如果需要）
sudo reboot
```

### 内容管理

#### 查看内容历史

```bash
# 创建内容历史查看器
cat > scripts/view_history.py << 'EOF'
#!/usr/bin/env python3
"""查看内容历史"""

import json
from pathlib import Path
from datetime import datetime

def view_word_history():
    """查看单词历史"""
    cache_file = Path('data/word_cache.json')
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        print("📚 单词历史记录:")
        for i, entry in enumerate(data[-10:], 1):  # 显示最近10个
            word = entry.get('word', 'Unknown')
            definition = entry.get('definition', '')[:50] + '...'
            print(f"  {i:2d}. {word:15} - {definition}")

def view_sentence_history():
    """查看句子历史"""
    cache_file = Path('data/sentence_cache.json')
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        print("\n💬 句子历史记录:")
        for i, entry in enumerate(data[-10:], 1):  # 显示最近10个
            sentence = entry.get('sentence', '')[:60] + '...'
            author = entry.get('author', 'Unknown')
            print(f"  {i:2d}. {sentence}")
            print(f"      — {author}")

if __name__ == "__main__":
    view_word_history()
    view_sentence_history()
EOF

chmod +x scripts/view_history.py

# 运行历史查看器
python3 scripts/view_history.py
```

#### 收藏功能

```bash
# 创建收藏管理器
cat > scripts/favorites.py << 'EOF'
#!/usr/bin/env python3
"""收藏管理器"""

import json
from pathlib import Path
from datetime import datetime

class FavoritesManager:
    def __init__(self):
        self.favorites_file = Path('data/favorites.json')
        self.load_favorites()
    
    def load_favorites(self):
        """加载收藏"""
        if self.favorites_file.exists():
            with open(self.favorites_file, 'r') as f:
                self.favorites = json.load(f)
        else:
            self.favorites = {'words': [], 'sentences': []}
    
    def save_favorites(self):
        """保存收藏"""
        with open(self.favorites_file, 'w') as f:
            json.dump(self.favorites, f, indent=2)
    
    def add_current_word(self):
        """收藏当前单词"""
        cache_file = Path('data/word_cache.json')
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            if data:
                current_word = data[-1]  # 最新的单词
                current_word['favorited_at'] = datetime.now().isoformat()
                self.favorites['words'].append(current_word)
                self.save_favorites()
                print(f"✅ 已收藏单词: {current_word.get('word', 'Unknown')}")
    
    def add_current_sentence(self):
        """收藏当前句子"""
        cache_file = Path('data/sentence_cache.json')
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            if data:
                current_sentence = data[-1]  # 最新的句子
                current_sentence['favorited_at'] = datetime.now().isoformat()
                self.favorites['sentences'].append(current_sentence)
                self.save_favorites()
                print(f"✅ 已收藏句子: {current_sentence.get('sentence', 'Unknown')[:50]}...")
    
    def list_favorites(self):
        """列出收藏"""
        print("⭐ 收藏的单词:")
        for i, word in enumerate(self.favorites['words'], 1):
            print(f"  {i:2d}. {word.get('word', 'Unknown'):15} - {word.get('definition', '')[:40]}...")
        
        print("\n⭐ 收藏的句子:")
        for i, sentence in enumerate(self.favorites['sentences'], 1):
            print(f"  {i:2d}. {sentence.get('sentence', '')[:60]}...")
            print(f"      — {sentence.get('author', 'Unknown')}")

def main():
    import sys
    manager = FavoritesManager()
    
    if len(sys.argv) < 2:
        print("用法: python3 scripts/favorites.py [word|sentence|list]")
        return
    
    action = sys.argv[1]
    if action == 'word':
        manager.add_current_word()
    elif action == 'sentence':
        manager.add_current_sentence()
    elif action == 'list':
        manager.list_favorites()
    else:
        print("无效的操作")

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/favorites.py

# 使用收藏功能
python3 scripts/favorites.py word      # 收藏当前单词
python3 scripts/favorites.py sentence  # 收藏当前句子
python3 scripts/favorites.py list      # 查看收藏列表
```

## 🔧 高级功能

### 自定义API源

#### 添加新的API源

```python
# 在 word_config.py 中添加自定义API
CUSTOM_APIS = {
    'my_word_api': {
        'url': 'https://my-api.com/word-of-day',
        'headers': {'Authorization': 'Bearer YOUR_TOKEN'},
        'transform_function': 'transform_my_api_data'
    }
}

def transform_my_api_data(raw_data):
    """转换自定义API数据格式"""
    return {
        'word': raw_data.get('term', ''),
        'phonetic': raw_data.get('pronunciation', ''),
        'definition': raw_data.get('meaning', ''),
        'example': raw_data.get('sample_sentence', ''),
        'part_of_speech': raw_data.get('word_type', ''),
        'difficulty': raw_data.get('level', 'intermediate')
    }
```

#### 配置API优先级

```python
# 设置API使用优先级
API_PRIORITY = [
    'wordnik',      # 首选
    'my_word_api',  # 备选1
    'local_cache'   # 最后备选
]
```

### 定时任务定制

#### 创建复杂的定时规则

```bash
# 编辑crontab
crontab -e

# 添加复杂的定时规则
# 工作日早上8点
0 8 * * 1-5 cd $HOME/daily-word-epaper && ./manage.sh update

# 周末上午10点
0 10 * * 6,7 cd $HOME/daily-word-epaper && ./manage.sh update

# 每天晚上9点（仅限周一到周五）
0 21 * * 1-5 cd $HOME/daily-word-epaper && ./manage.sh update

# 每月1号更新系统
0 2 1 * * cd $HOME/daily-word-epaper && ./scripts/system_update.sh
```

#### 智能更新策略

```bash
# 创建智能更新脚本
cat > scripts/smart_update.py << 'EOF'
#!/usr/bin/env python3
"""智能更新策略"""

import json
from datetime import datetime, time
from pathlib import Path

class SmartUpdater:
    def __init__(self):
        self.config_file = Path('data/smart_config.json')
        self.load_config()
    
    def load_config(self):
        """加载智能配置"""
        default_config = {
            'weekday_times': ['07:30', '12:00', '18:30'],
            'weekend_times': ['09:00', '15:00'],
            'holiday_times': ['10:00'],
            'quiet_hours': ['22:00', '06:00'],  # 静默时间段
            'adaptive_frequency': True,         # 自适应频率
            'weather_based': False             # 基于天气调整
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def should_update_now(self):
        """判断是否应该现在更新"""
        now = datetime.now()
        current_time = now.time()
        
        # 检查静默时间
        if self.is_quiet_time(current_time):
            return False
        
        # 根据日期类型选择更新时间
        if now.weekday() < 5:  # 工作日
            target_times = self.config['weekday_times']
        else:  # 周末
            target_times = self.config['weekend_times']
        
        # 检查是否在更新时间窗口内（±15分钟）
        for time_str in target_times:
            target_time = datetime.strptime(time_str, '%H:%M').time()
            if self.is_time_window(current_time, target_time, 15):
                return True
        
        return False
    
    def is_quiet_time(self, current_time):
        """检查是否在静默时间"""
        start_str, end_str = self.config['quiet_hours']
        start_time = datetime.strptime(start_str, '%H:%M').time()
        end_time = datetime.strptime(end_str, '%H:%M').time()
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:  # 跨午夜
            return current_time >= start_time or current_time <= end_time
    
    def is_time_window(self, current, target, window_minutes):
        """检查是否在时间窗口内"""
        current_minutes = current.hour * 60 + current.minute
        target_minutes = target.hour * 60 + target.minute
        return abs(current_minutes - target_minutes) <= window_minutes

def main():
    updater = SmartUpdater()
    if updater.should_update_now():
        print("✅ 执行更新")
        import subprocess
        subprocess.run(['./manage.sh', 'update'])
    else:
        print("⏸️ 跳过更新")

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/smart_update.py

# 使用智能更新（替换原有的cron任务）
# */15 * * * * cd $HOME/daily-word-epaper && python3 scripts/smart_update.py
```

### 多设备同步

#### 设置设备同步

```bash
# 创建同步管理器
cat > scripts/sync_manager.py << 'EOF'
#!/usr/bin/env python3
"""多设备同步管理器"""

import json
import requests
from pathlib import Path
from datetime import datetime

class SyncManager:
    def __init__(self):
        self.config_file = Path('data/sync_config.json')
        self.load_config()
    
    def load_config(self):
        """加载同步配置"""
        default_config = {
            'sync_enabled': False,
            'sync_server': 'https://your-sync-server.com',
            'device_id': 'device_001',
            'sync_interval': 3600,  # 1小时
            'last_sync': None
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def upload_content(self):
        """上传当前内容到同步服务器"""
        if not self.config['sync_enabled']:
            return False
        
        # 读取当前内容
        word_cache = Path('data/word_cache.json')
        sentence_cache = Path('data/sentence_cache.json')
        
        sync_data = {
            'device_id': self.config['device_id'],
            'timestamp': datetime.now().isoformat(),
            'word_data': {},
            'sentence_data': {}
        }
        
        if word_cache.exists():
            with open(word_cache, 'r') as f:
                sync_data['word_data'] = json.load(f)
        
        if sentence_cache.exists():
            with open(sentence_cache, 'r') as f:
                sync_data['sentence_data'] = json.load(f)
        
        try:
            response = requests.post(
                f"{self.config['sync_server']}/upload",
                json=sync_data,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"同步上传失败: {e}")
            return False
    
    def download_content(self):
        """从同步服务器下载内容"""
        if not self.config['sync_enabled']:
            return False
        
        try:
            response = requests.get(
                f"{self.config['sync_server']}/download",
                params={'device_id': self.config['device_id']},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 保存下载的内容
                if data.get('word_data'):
                    with open('data/word_cache.json', 'w') as f:
                        json.dump(data['word_data'], f)
                
                if data.get('sentence_data'):
                    with open('data/sentence_cache.json', 'w') as f:
                        json.dump(data['sentence_data'], f)
                
                return True
        except Exception as e:
            print(f"同步下载失败: {e}")
        
        return False

def main():
    import sys
    manager = SyncManager()
    
    if len(sys.argv) < 2:
        print("用法: python3 scripts/sync_manager.py [upload|download]")
        return
    
    action = sys.argv[1]
    if action == 'upload':
        success = manager.upload_content()
        print("✅ 上传成功" if success else "❌ 上传失败")
    elif action == 'download':
        success = manager.download_content()
        print("✅ 下载成功" if success else "❌ 下载失败")

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/sync_manager.py
```

## 📊 统计和分析

### 学习统计

```bash
# 创建学习统计器
cat > scripts/learning_stats.py << 'EOF'
#!/usr/bin/env python3
"""学习统计分析"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

class LearningStats:
    def __init__(self):
        self.word_cache = Path('data/word_cache.json')
        self.sentence_cache = Path('data/sentence_cache.json')
        self.favorites_file = Path('data/favorites.json')
    
    def get_word_stats(self):
        """获取单词学习统计"""
        if not self.word_cache.exists():
            return {}
        
        with open(self.word_cache, 'r') as f:
            words = json.load(f)
        
        # 统计词性分布
        pos_counter = Counter()
        difficulty_counter = Counter()
        length_counter = Counter()
        
        for word_data in words:
            pos = word_data.get('part_of_speech', 'unknown')
            difficulty = word_data.get('difficulty', 'unknown')
            word_length = len(word_data.get('word', ''))
            
            pos_counter[pos] += 1
            difficulty_counter[difficulty] += 1
            
            if word_length <= 5:
                length_counter['short'] += 1
            elif word_length <= 8:
                length_counter['medium'] += 1
            else:
                length_counter['long'] += 1
        
        return {
            'total_words': len(words),
            'part_of_speech': dict(pos_counter),
            'difficulty': dict(difficulty_counter),
            'length_distribution': dict(length_counter)
        }
    
    def get_sentence_stats(self):
        """获取句子学习统计"""
        if not self.sentence_cache.exists():
            return {}
        
        with open(self.sentence_cache, 'r') as f:
            sentences = json.load(f)
        
        # 统计作者和分类
        author_counter = Counter()
        category_counter = Counter()
        
        for sentence_data in sentences:
            author = sentence_data.get('author', 'unknown')
            category = sentence_data.get('category', 'unknown')
            
            author_counter[author] += 1
            category_counter[category] += 1
        
        return {
            'total_sentences': len(sentences),
            'top_authors': dict(author_counter.most_common(5)),
            'categories': dict(category_counter)
        }
    
    def get_learning_progress(self):
        """获取学习进度"""
        # 计算最近7天、30天的学习情况
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        progress = {
            'this_week': 0,
            'this_month': 0,
            'favorites_count': 0
        }
        
        # 统计收藏数量
        if self.favorites_file.exists():
            with open(self.favorites_file, 'r') as f:
                favorites = json.load(f)
                progress['favorites_count'] = (
                    len(favorites.get('words', [])) + 
                    len(favorites.get('sentences', []))
                )
        
        return progress
    
    def generate_report(self):
        """生成学习报告"""
        word_stats = self.get_word_stats()
        sentence_stats = self.get_sentence_stats()
        progress = self.get_learning_progress()
        
        print("=" * 50)
        print("📊 学习统计报告")
        print("=" * 50)
        
        # 单词统计
        print(f"\n📚 单词学习统计:")
        print(f"  总学习单词: {word_stats.get('total_words', 0)} 个")
        
        if word_stats.get('difficulty'):
            print(f"  难度分布:")
            for difficulty, count in word_stats['difficulty'].items():
                print(f"    {difficulty}: {count} 个")
        
        if word_stats.get('part_of_speech'):
            print(f"  词性分布:")
            for pos, count in word_stats['part_of_speech'].items():
                print(f"    {pos}: {count} 个")
        
        # 句子统计
        print(f"\n💬 句子学习统计:")
        print(f"  总学习句子: {sentence_stats.get('total_sentences', 0)} 条")
        
        if sentence_stats.get('top_authors'):
            print(f"  热门作者:")
            for author, count in sentence_stats['top_authors'].items():
                print(f"    {author}: {count} 条")
        
        # 学习进度
        print(f"\n📈 学习进度:")
        print(f"  收藏总数: {progress['favorites_count']} 项")
        print(f"  本周学习: {progress['this_week']} 次")
        print(f"  本月学习: {progress['this_month']} 次")
        
        print("\n" + "=" * 50)

def main():
    stats = LearningStats()
    stats.generate_report()

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/learning_stats.py

# 查看学习统计
python3 scripts/learning_stats.py
```

## 🛠️ 故障处理

### 常见问题自助解决

#### 显示问题

```bash
# 如果墨水屏无显示
./manage.sh clear    # 清空显示
./manage.sh test     # 运行测试
./manage.sh restart  # 重启服务

# 如果显示内容异常
python3 scripts/diagnose.py  # 运行诊断
python3 scripts/auto_fix.py  # 自动修复
```

#### 网络问题

```bash
# 如果无法获取内容
ping 8.8.8.8                    # 测试网络连接
curl -I https://api.quotable.io # 测试API连接

# 启用本地备用内容
nano src/word_config.py
# 设置: USE_LOCAL_FALLBACK = True
./manage.sh restart
```

#### 服务问题

```bash
# 如果服务无法启动
sudo systemctl status daily-word  # 查看服务状态
sudo journalctl -u daily-word     # 查看服务日志
./scripts/auto_fix.py             # 运行自动修复
```

### 获取帮助

如果遇到无法解决的问题：

1. **查看日志**
   ```bash
   ./manage.sh logs
   ```

2. **运行诊断**
   ```bash
   python3 scripts/diagnose.py
   ```

3. **收集支持信息**
   ```bash
   ./scripts/collect_logs.sh
   ```

4. **联系支持**
   - 查看故障排除文档
   - 访问项目GitHub页面
   - 联系技术支持

## 📋 使用技巧

### 最佳实践

1. **定期维护**
   - 每周检查系统状态
   - 定期清理日志文件
   - 及时更新系统软件

2. **个性化设置**
   - 根据使用习惯调整更新时间
   - 选择合适的字体大小
   - 设置喜欢的内容类型

3. **备份重要数据**
   - 定期备份配置文件
   - 保存收藏的内容
   - 备份自定义设置

4. **监控系统性能**
   - 关注CPU和内存使用
   - 监控网络连接状态
   - 检查墨水屏显示质量

### 快捷操作

```bash
# 创建快捷命令别名
echo 'alias dw="cd ~/daily-word-epaper"' >> ~/.bashrc
echo 'alias dwstatus="cd ~/daily-word-epaper && ./manage.sh status"' >> ~/.bashrc
echo 'alias dwupdate="cd ~/daily-word-epaper && ./manage.sh update"' >> ~/.bashrc
echo 'alias dwlogs="cd ~/daily-word-epaper && ./manage.sh logs"' >> ~/.bashrc

# 重新加载配置
source ~/.bashrc

# 现在可以使用简短命令
dwstatus  # 查看状态
dwupdate  # 更新内容
dwlogs    # 查看日志
```

---

**恭喜！** 您已经掌握了每日单词墨水屏显示系统的完整使用方法。享受您的学习之旅！