# 部署和运行

## 📋 概述

本章节将指导您部署和运行每日单词墨水屏显示系统，包括首次启动、服务配置、定时任务设置和运行验证。

## 🚀 首次启动

### 预启动检查

在首次启动前，请确认以下项目：

```bash
# 检查项目目录
ls -la ~/daily-word-epaper/
# 应该看到: src/, data/, logs/, venv/, manage.sh

# 检查配置文件
ls -la ~/daily-word-epaper/src/word_config.py

# 检查虚拟环境
ls -la ~/daily-word-epaper/venv/

# 检查权限
ls -la ~/daily-word-epaper/src/*.py
# 应该有执行权限 (-rwxr-xr-x)
```

### 激活虚拟环境

```bash
cd ~/daily-word-epaper
source venv/bin/activate

# 验证Python环境
which python3
# 应该显示: /home/pi/daily-word-epaper/venv/bin/python3
```

### 运行首次测试

```bash
# 运行基础测试
python3 src/daily_word_rpi.py --test

# 预期输出示例:
# === 每日单词系统启动 ===
# 墨水屏显示器初始化成功
# 开始获取每日单词和句子...
# 成功获取每日单词: example
# ✅ 测试通过
```

## 🔧 运行模式

系统支持多种运行模式，根据不同需求选择合适的模式：

### 1. 单次运行模式

适用于测试和手动更新：

```bash
# 运行一次更新
python3 src/daily_word_rpi.py --mode once

# 或使用管理脚本
./manage.sh update
```

### 2. 定时运行模式

适用于cron定时任务：

```bash
# 定时运行（适合cron调用）
python3 src/daily_word_rpi.py --mode scheduled

# 运行后自动进入睡眠模式节省电力
```

### 3. 守护进程模式

持续运行，自动在指定时间更新：

```bash
# 启动守护进程
python3 src/daily_word_rpi.py --mode daemon

# 后台运行
nohup python3 src/daily_word_rpi.py --mode daemon > /dev/null 2>&1 &
```

### 4. 测试模式

用于调试和验证：

```bash
# 测试模式（不实际显示到墨水屏）
python3 src/daily_word_rpi.py --test

# 清空显示
python3 src/daily_word_rpi.py --clear
```

## 🛠️ 服务管理

### systemd服务配置

#### 创建服务文件

```bash
# 创建systemd服务文件
sudo tee /etc/systemd/system/daily-word.service > /dev/null <<EOF
[Unit]
Description=Daily Word E-Paper Display Service
Documentation=https://github.com/your-repo/daily-word-epaper
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$HOME/daily-word-epaper
Environment=PATH=$HOME/daily-word-epaper/venv/bin
Environment=PYTHONPATH=$HOME/daily-word-epaper/src
ExecStart=$HOME/daily-word-epaper/venv/bin/python $HOME/daily-word-epaper/src/daily_word_rpi.py --mode daemon
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
Restart=on-failure
RestartSec=30
TimeoutStopSec=20

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$HOME/daily-word-epaper

# 资源限制
MemoryMax=256M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
EOF
```

#### 服务管理命令

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start daily-word

# 停止服务
sudo systemctl stop daily-word

# 重启服务
sudo systemctl restart daily-word

# 查看服务状态
sudo systemctl status daily-word

# 启用开机自启
sudo systemctl enable daily-word

# 禁用开机自启
sudo systemctl disable daily-word

# 查看服务日志
sudo journalctl -u daily-word -f
```

### 使用管理脚本

系统提供了便捷的管理脚本：

```bash
# 查看所有可用命令
./manage.sh

# 服务管理
./manage.sh start      # 启动服务
./manage.sh stop       # 停止服务
./manage.sh restart    # 重启服务
./manage.sh status     # 查看状态
./manage.sh enable     # 启用自启
./manage.sh disable    # 禁用自启

# 功能操作
./manage.sh update     # 手动更新显示
./manage.sh test       # 运行测试
./manage.sh clear      # 清空显示
./manage.sh logs       # 查看日志
```

## ⏰ 定时任务配置

### cron定时任务

#### 创建定时任务

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每日8点、12点、18点更新）
0 8,12,18 * * * cd $HOME/daily-word-epaper && ./venv/bin/python src/daily_word_rpi.py --mode scheduled >> logs/cron.log 2>&1

# 添加每日重启任务（可选，凌晨4点重启）
0 4 * * * sudo reboot

# 添加日志清理任务（每周清理一次）
0 2 * * 0 find $HOME/daily-word-epaper/logs -name "*.log" -mtime +7 -delete
```

#### 验证定时任务

```bash
# 查看当前定时任务
crontab -l

# 查看cron日志
tail -f /var/log/cron.log

# 查看应用日志
tail -f ~/daily-word-epaper/logs/cron.log
```

### systemd定时器（推荐）

#### 创建定时器配置

```bash
# 创建定时器服务文件
sudo tee /etc/systemd/system/daily-word-update.service > /dev/null <<EOF
[Unit]
Description=Daily Word Update
Requires=daily-word-update.timer

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$HOME/daily-word-epaper
Environment=PATH=$HOME/daily-word-epaper/venv/bin
ExecStart=$HOME/daily-word-epaper/venv/bin/python $HOME/daily-word-epaper/src/daily_word_rpi.py --mode scheduled

[Install]
WantedBy=multi-user.target
EOF

# 创建定时器文件
sudo tee /etc/systemd/system/daily-word-update.timer > /dev/null <<EOF
[Unit]
Description=Daily Word Update Timer
Requires=daily-word-update.service

[Timer]
OnCalendar=*-*-* 08,12,18:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
```

#### 启用定时器

```bash
# 重新加载配置
sudo systemctl daemon-reload

# 启用并启动定时器
sudo systemctl enable daily-word-update.timer
sudo systemctl start daily-word-update.timer

# 查看定时器状态
sudo systemctl status daily-word-update.timer

# 查看下次执行时间
sudo systemctl list-timers daily-word-update.timer
```

## 📊 运行监控

### 系统状态监控

#### 创建监控脚本

```bash
cat > scripts/monitor.py << 'EOF'
#!/usr/bin/env python3
"""
系统监控脚本
监控系统运行状态和性能指标
"""

import psutil
import time
import json
from pathlib import Path
from datetime import datetime

def get_system_info():
    """获取系统信息"""
    return {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'temperature': get_cpu_temperature(),
        'uptime': time.time() - psutil.boot_time()
    }

def get_cpu_temperature():
    """获取CPU温度"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read()) / 1000.0
            return temp
    except:
        return None

def check_service_status():
    """检查服务状态"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', 'daily-word'],
            capture_output=True, text=True
        )
        return result.stdout.strip() == 'active'
    except:
        return False

def save_metrics(metrics):
    """保存监控指标"""
    metrics_file = Path('data/metrics.json')
    
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            data = json.load(f)
    else:
        data = []
    
    data.append(metrics)
    
    # 只保留最近100条记录
    if len(data) > 100:
        data = data[-100:]
    
    with open(metrics_file, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    """主函数"""
    metrics = get_system_info()
    metrics['service_active'] = check_service_status()
    
    print(f"时间: {metrics['timestamp']}")
    print(f"CPU使用率: {metrics['cpu_percent']:.1f}%")
    print(f"内存使用率: {metrics['memory_percent']:.1f}%")
    print(f"磁盘使用率: {metrics['disk_percent']:.1f}%")
    
    if metrics['temperature']:
        print(f"CPU温度: {metrics['temperature']:.1f}°C")
    
    print(f"服务状态: {'运行中' if metrics['service_active'] else '已停止'}")
    
    save_metrics(metrics)

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/monitor.py
```

#### 运行监控

```bash
# 手动运行监控
python3 scripts/monitor.py

# 添加到cron定时监控（每5分钟）
echo "*/5 * * * * cd $HOME/daily-word-epaper && python3 scripts/monitor.py >> logs/monitor.log 2>&1" | crontab -
```

### 日志监控

#### 实时日志查看

```bash
# 查看应用日志
tail -f data/daily_word.log

# 查看系统服务日志
sudo journalctl -u daily-word -f

# 查看cron日志
tail -f logs/cron.log

# 查看监控日志
tail -f logs/monitor.log
```

#### 日志分析脚本

```bash
cat > scripts/analyze_logs.py << 'EOF'
#!/usr/bin/env python3
"""
日志分析脚本
分析系统运行日志，生成统计报告
"""

import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta

def analyze_log_file(log_file):
    """分析日志文件"""
    if not log_file.exists():
        return {}
    
    stats = {
        'total_lines': 0,
        'error_count': 0,
        'warning_count': 0,
        'success_count': 0,
        'recent_errors': [],
        'error_types': Counter()
    }
    
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            stats['total_lines'] += 1
            
            if 'ERROR' in line:
                stats['error_count'] += 1
                stats['recent_errors'].append(line.strip())
                
                # 提取错误类型
                error_match = re.search(r'ERROR.*?(\w+Error|\w+Exception)', line)
                if error_match:
                    stats['error_types'][error_match.group(1)] += 1
            
            elif 'WARNING' in line:
                stats['warning_count'] += 1
            
            elif '成功' in line or 'SUCCESS' in line:
                stats['success_count'] += 1
    
    # 只保留最近10条错误
    stats['recent_errors'] = stats['recent_errors'][-10:]
    
    return stats

def generate_report():
    """生成分析报告"""
    log_file = Path('data/daily_word.log')
    stats = analyze_log_file(log_file)
    
    print("=== 日志分析报告 ===")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"日志文件: {log_file}")
    print()
    
    print("📊 统计信息:")
    print(f"  总行数: {stats['total_lines']}")
    print(f"  错误数: {stats['error_count']}")
    print(f"  警告数: {stats['warning_count']}")
    print(f"  成功数: {stats['success_count']}")
    print()
    
    if stats['error_types']:
        print("🚨 错误类型分布:")
        for error_type, count in stats['error_types'].most_common():
            print(f"  {error_type}: {count}次")
        print()
    
    if stats['recent_errors']:
        print("📝 最近错误:")
        for error in stats['recent_errors']:
            print(f"  {error}")
        print()
    
    # 计算成功率
    total_operations = stats['success_count'] + stats['error_count']
    if total_operations > 0:
        success_rate = (stats['success_count'] / total_operations) * 100
        print(f"✅ 成功率: {success_rate:.1f}%")

if __name__ == "__main__":
    generate_report()
EOF

chmod +x scripts/analyze_logs.py
```

## 🔍 运行验证

### 功能验证清单

完成部署后，请按以下清单验证系统功能：

#### 基础功能验证

```bash
# 1. 测试单次运行
./manage.sh test
# ✅ 应该显示测试通过

# 2. 测试手动更新
./manage.sh update
# ✅ 应该成功获取并显示内容

# 3. 测试服务启动
./manage.sh start
./manage.sh status
# ✅ 服务应该处于active状态

# 4. 测试日志记录
./manage.sh logs
# ✅ 应该看到正常的日志输出
```

#### 硬件功能验证

```bash
# 1. 测试墨水屏显示
python3 -c "
from src.epaper_display_rpi import EPaperDisplay
display = EPaperDisplay()
print('✅ 墨水屏初始化成功' if display.epd else '❌ 墨水屏初始化失败')
"

# 2. 测试GPIO控制
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.HIGH)
GPIO.cleanup()
print('✅ GPIO控制正常')
"

# 3. 测试SPI通信
python3 -c "
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
spi.close()
print('✅ SPI通信正常')
"
```

#### 网络功能验证

```bash
# 1. 测试API连接
python3 -c "
import requests
from src.word_config import WORD_API_CONFIG
try:
    response = requests.get(WORD_API_CONFIG['sentence_api_url'], timeout=5)
    print('✅ API连接正常')
except Exception as e:
    print(f'❌ API连接失败: {e}')
"

# 2. 测试内容获取
python3 -c "
from src.class_word_api import WordAPI
api = WordAPI()
success = api.get_daily_content()
print('✅ 内容获取成功' if success else '❌ 内容获取失败')
"
```

### 性能基准测试

```bash
# 创建性能测试脚本
cat > scripts/benchmark.py << 'EOF'
#!/usr/bin/env python3
"""
性能基准测试
测试系统各项功能的性能指标
"""

import time
import psutil
from src.class_word_api import WordAPI
from src.epaper_display_rpi import EPaperDisplay

def measure_time(func):
    """测量函数执行时间"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    return wrapper

@measure_time
def test_api_performance():
    """测试API性能"""
    api = WordAPI()
    return api.get_daily_content()

@measure_time
def test_display_performance():
    """测试显示性能"""
    display = EPaperDisplay()
    word_data = {'word': 'test', 'definition': 'test definition'}
    sentence_data = {'sentence': 'test sentence', 'author': 'test author'}
    return display.display_content(word_data, sentence_data)

def run_benchmark():
    """运行基准测试"""
    print("=== 性能基准测试 ===")
    
    # 记录初始系统状态
    initial_memory = psutil.virtual_memory().percent
    initial_cpu = psutil.cpu_percent(interval=1)
    
    print(f"初始内存使用: {initial_memory:.1f}%")
    print(f"初始CPU使用: {initial_cpu:.1f}%")
    print()
    
    # API性能测试
    print("测试API性能...")
    api_result, api_time = test_api_performance()
    print(f"API请求时间: {api_time:.2f}秒")
    print(f"API请求结果: {'成功' if api_result else '失败'}")
    print()
    
    # 显示性能测试
    print("测试显示性能...")
    display_result, display_time = test_display_performance()
    print(f"显示更新时间: {display_time:.2f}秒")
    print(f"显示更新结果: {'成功' if display_result else '失败'}")
    print()
    
    # 记录最终系统状态
    final_memory = psutil.virtual_memory().percent
    final_cpu = psutil.cpu_percent(interval=1)
    
    print(f"最终内存使用: {final_memory:.1f}%")
    print(f"最终CPU使用: {final_cpu:.1f}%")
    print(f"内存变化: {final_memory - initial_memory:+.1f}%")
    print()
    
    # 性能评估
    total_time = api_time + display_time
    print("=== 性能评估 ===")
    print(f"总执行时间: {total_time:.2f}秒")
    
    if total_time < 30:
        print("✅ 性能优秀")
    elif total_time < 60:
        print("⚠️ 性能良好")
    else:
        print("❌ 性能需要优化")

if __name__ == "__main__":
    run_benchmark()
EOF

chmod +x scripts/benchmark.py

# 运行性能测试
python3 scripts/benchmark.py
```

## 📋 部署检查清单

完成部署后，请确认以下项目：

### 基础部署
- [ ] 项目文件完整
- [ ] 虚拟环境正常
- [ ] 配置文件正确
- [ ] 权限设置正确

### 服务配置
- [ ] systemd服务已创建
- [ ] 服务可以正常启动
- [ ] 开机自启已配置
- [ ] 管理脚本可用

### 定时任务
- [ ] cron任务已设置
- [ ] 定时器正常工作
- [ ] 日志轮转已配置
- [ ] 监控脚本运行

### 功能验证
- [ ] 单次运行正常
- [ ] 手动更新成功
- [ ] 墨水屏显示正常
- [ ] API连接正常
- [ ] 日志记录正常

### 性能监控
- [ ] 系统监控正常
- [ ] 性能指标合理
- [ ] 错误率可接受
- [ ] 资源使用正常

---

**下一步：** [维护管理](06-maintenance.md)