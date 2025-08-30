# 维护管理

## 📋 概述

本章节提供系统的日常维护、监控、备份、更新和故障处理指南，确保系统长期稳定运行。

## 🔧 日常维护

### 系统健康检查

#### 每日检查项目

```bash
# 创建每日检查脚本
cat > scripts/daily_check.sh << 'EOF'
#!/bin/bash
# 每日系统健康检查脚本

echo "=== 每日系统健康检查 $(date) ==="

# 1. 检查服务状态
echo "📊 服务状态检查:"
if systemctl is-active --quiet daily-word; then
    echo "  ✅ daily-word服务: 运行中"
else
    echo "  ❌ daily-word服务: 已停止"
fi

# 2. 检查磁盘空间
echo "💾 磁盘空间检查:"
df -h / | awk 'NR==2 {
    if ($5+0 > 90) 
        print "  ❌ 磁盘使用率过高: " $5
    else if ($5+0 > 80)
        print "  ⚠️ 磁盘使用率较高: " $5
    else
        print "  ✅ 磁盘使用率正常: " $5
}'

# 3. 检查内存使用
echo "🧠 内存使用检查:"
free | awk 'NR==2 {
    used_percent = $3/$2 * 100
    if (used_percent > 90)
        print "  ❌ 内存使用率过高: " int(used_percent) "%"
    else if (used_percent > 80)
        print "  ⚠️ 内存使用率较高: " int(used_percent) "%"
    else
        print "  ✅ 内存使用率正常: " int(used_percent) "%"
}'

# 4. 检查CPU温度
echo "🌡️ CPU温度检查:"
if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    temp=$(cat /sys/class/thermal/thermal_zone0/temp)
    temp_c=$((temp/1000))
    if [ $temp_c -gt 80 ]; then
        echo "  ❌ CPU温度过高: ${temp_c}°C"
    elif [ $temp_c -gt 70 ]; then
        echo "  ⚠️ CPU温度较高: ${temp_c}°C"
    else
        echo "  ✅ CPU温度正常: ${temp_c}°C"
    fi
fi

# 5. 检查最近错误
echo "📝 最近错误检查:"
error_count=$(grep -c "ERROR" data/daily_word.log 2>/dev/null || echo "0")
if [ $error_count -gt 10 ]; then
    echo "  ❌ 发现 $error_count 个错误，需要检查"
elif [ $error_count -gt 5 ]; then
    echo "  ⚠️ 发现 $error_count 个错误，建议检查"
else
    echo "  ✅ 错误数量正常: $error_count"
fi

# 6. 检查网络连接
echo "🌐 网络连接检查:"
if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    echo "  ✅ 网络连接正常"
else
    echo "  ❌ 网络连接异常"
fi

echo "=== 检查完成 ==="
echo
EOF

chmod +x scripts/daily_check.sh
```

#### 运行每日检查

```bash
# 手动运行检查
./scripts/daily_check.sh

# 添加到cron定时检查（每天早上8点）
echo "0 8 * * * cd $HOME/daily-word-epaper && ./scripts/daily_check.sh >> logs/health_check.log 2>&1" | crontab -
```

### 日志管理

#### 日志轮转配置

```bash
# 创建logrotate配置
sudo tee /etc/logrotate.d/daily-word << 'EOF'
/home/pi/daily-word-epaper/data/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 pi pi
    postrotate
        systemctl reload daily-word 2>/dev/null || true
    endscript
}

/home/pi/daily-word-epaper/logs/*.log {
    weekly
    missingok
    rotate 12
    compress
    delaycompress
    notifempty
    create 644 pi pi
}
EOF
```

#### 手动日志清理

```bash
# 创建日志清理脚本
cat > scripts/cleanup_logs.sh << 'EOF'
#!/bin/bash
# 日志清理脚本

echo "=== 开始清理日志 $(date) ==="

# 清理超过30天的应用日志
find data/ -name "*.log" -mtime +30 -delete
echo "✅ 清理应用日志完成"

# 清理超过7天的cron日志
find logs/ -name "*.log" -mtime +7 -delete
echo "✅ 清理cron日志完成"

# 清理超过3天的临时文件
find /tmp -name "daily_word_*" -mtime +3 -delete 2>/dev/null
echo "✅ 清理临时文件完成"

# 压缩大于10MB的日志文件
find data/ logs/ -name "*.log" -size +10M -exec gzip {} \;
echo "✅ 压缩大日志文件完成"

echo "=== 日志清理完成 ==="
EOF

chmod +x scripts/cleanup_logs.sh

# 添加到cron（每周日凌晨2点执行）
echo "0 2 * * 0 cd $HOME/daily-word-epaper && ./scripts/cleanup_logs.sh >> logs/cleanup.log 2>&1" | crontab -
```

### 系统更新

#### 系统软件更新

```bash
# 创建系统更新脚本
cat > scripts/system_update.sh << 'EOF'
#!/bin/bash
# 系统更新脚本

echo "=== 开始系统更新 $(date) ==="

# 更新包列表
echo "📦 更新包列表..."
sudo apt update

# 升级系统包
echo "⬆️ 升级系统包..."
sudo apt upgrade -y

# 清理不需要的包
echo "🧹 清理系统..."
sudo apt autoremove -y
sudo apt autoclean

# 更新Python包
echo "🐍 更新Python包..."
cd ~/daily-word-epaper
source venv/bin/activate
pip install --upgrade pip
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U

echo "=== 系统更新完成 ==="
EOF

chmod +x scripts/system_update.sh
```

#### 应用程序更新

```bash
# 创建应用更新脚本
cat > scripts/app_update.sh << 'EOF'
#!/bin/bash
# 应用程序更新脚本

echo "=== 开始应用更新 $(date) ==="

# 备份当前配置
echo "💾 备份当前配置..."
cp src/word_config.py src/word_config.py.backup.$(date +%Y%m%d_%H%M%S)

# 拉取最新代码（如果使用git）
if [ -d .git ]; then
    echo "📥 拉取最新代码..."
    git stash
    git pull origin main
    git stash pop
fi

# 更新Python依赖
echo "🐍 更新Python依赖..."
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 重启服务
echo "🔄 重启服务..."
sudo systemctl restart daily-word

# 验证更新
echo "✅ 验证更新..."
sleep 5
if systemctl is-active --quiet daily-word; then
    echo "✅ 服务重启成功"
else
    echo "❌ 服务重启失败，回滚配置"
    # 回滚逻辑
    latest_backup=$(ls -t src/word_config.py.backup.* | head -1)
    if [ -f "$latest_backup" ]; then
        cp "$latest_backup" src/word_config.py
        sudo systemctl restart daily-word
    fi
fi

echo "=== 应用更新完成 ==="
EOF

chmod +x scripts/app_update.sh
```

## 💾 备份与恢复

### 自动备份

#### 创建备份脚本

```bash
# 创建备份脚本
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
# 系统备份脚本

BACKUP_DIR="$HOME/daily-word-backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="daily-word-backup-$DATE"

echo "=== 开始备份 $(date) ==="

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 创建临时备份目录
TEMP_BACKUP="$BACKUP_DIR/$BACKUP_NAME"
mkdir -p "$TEMP_BACKUP"

# 备份应用文件
echo "📁 备份应用文件..."
cp -r src/ "$TEMP_BACKUP/"
cp -r data/ "$TEMP_BACKUP/"
cp -r scripts/ "$TEMP_BACKUP/"
cp requirements.txt "$TEMP_BACKUP/" 2>/dev/null || true
cp manage.sh "$TEMP_BACKUP/" 2>/dev/null || true

# 备份配置文件
echo "⚙️ 备份配置文件..."
mkdir -p "$TEMP_BACKUP/config"
sudo cp /etc/systemd/system/daily-word.service "$TEMP_BACKUP/config/" 2>/dev/null || true
sudo cp /etc/systemd/system/daily-word-update.* "$TEMP_BACKUP/config/" 2>/dev/null || true
crontab -l > "$TEMP_BACKUP/config/crontab.txt" 2>/dev/null || true

# 备份日志（最近7天）
echo "📝 备份最近日志..."
mkdir -p "$TEMP_BACKUP/logs"
find logs/ -name "*.log" -mtime -7 -exec cp {} "$TEMP_BACKUP/logs/" \; 2>/dev/null || true

# 创建备份信息文件
echo "📋 创建备份信息..."
cat > "$TEMP_BACKUP/backup_info.txt" << EOL
备份时间: $(date)
备份版本: $DATE
系统信息: $(uname -a)
Python版本: $(python3 --version)
磁盘使用: $(df -h /)
内存信息: $(free -h)
服务状态: $(systemctl is-active daily-word 2>/dev/null || echo "未知")
EOL

# 压缩备份
echo "🗜️ 压缩备份文件..."
cd "$BACKUP_DIR"
tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# 清理旧备份（保留最近10个）
echo "🧹 清理旧备份..."
ls -t daily-word-backup-*.tar.gz | tail -n +11 | xargs rm -f

echo "✅ 备份完成: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo "=== 备份结束 ==="
EOF

chmod +x scripts/backup.sh

# 添加到cron（每天凌晨3点备份）
echo "0 3 * * * cd $HOME/daily-word-epaper && ./scripts/backup.sh >> logs/backup.log 2>&1" | crontab -
```

### 恢复系统

#### 创建恢复脚本

```bash
# 创建恢复脚本
cat > scripts/restore.sh << 'EOF'
#!/bin/bash
# 系统恢复脚本

if [ $# -ne 1 ]; then
    echo "用法: $0 <备份文件路径>"
    echo "示例: $0 ~/daily-word-backups/daily-word-backup-20240830_030000.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="/tmp/daily-word-restore-$$"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "=== 开始恢复 $(date) ==="
echo "📁 备份文件: $BACKUP_FILE"

# 停止服务
echo "⏹️ 停止服务..."
sudo systemctl stop daily-word 2>/dev/null || true

# 创建临时恢复目录
mkdir -p "$RESTORE_DIR"

# 解压备份文件
echo "📦 解压备份文件..."
cd "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE"

# 找到备份目录
BACKUP_CONTENT=$(find . -maxdepth 1 -type d -name "daily-word-backup-*" | head -1)
if [ -z "$BACKUP_CONTENT" ]; then
    echo "❌ 无效的备份文件格式"
    rm -rf "$RESTORE_DIR"
    exit 1
fi

cd "$BACKUP_CONTENT"

# 备份当前系统（以防恢复失败）
echo "💾 备份当前系统..."
CURRENT_BACKUP="$HOME/daily-word-epaper-current-$(date +%Y%m%d_%H%M%S)"
cp -r "$HOME/daily-word-epaper" "$CURRENT_BACKUP"

# 恢复应用文件
echo "📁 恢复应用文件..."
cp -r src/* "$HOME/daily-word-epaper/src/"
cp -r data/* "$HOME/daily-word-epaper/data/" 2>/dev/null || true
cp -r scripts/* "$HOME/daily-word-epaper/scripts/" 2>/dev/null || true
cp requirements.txt "$HOME/daily-word-epaper/" 2>/dev/null || true
cp manage.sh "$HOME/daily-word-epaper/" 2>/dev/null || true

# 恢复配置文件
echo "⚙️ 恢复配置文件..."
if [ -d config ]; then
    sudo cp config/daily-word.service /etc/systemd/system/ 2>/dev/null || true
    sudo cp config/daily-word-update.* /etc/systemd/system/ 2>/dev/null || true
    
    if [ -f config/crontab.txt ]; then
        echo "恢复cron任务? (y/n)"
        read -r response
        if [ "$response" = "y" ]; then
            crontab config/crontab.txt
        fi
    fi
fi

# 重新加载systemd
echo "🔄 重新加载systemd..."
sudo systemctl daemon-reload

# 启动服务
echo "▶️ 启动服务..."
sudo systemctl start daily-word

# 验证恢复
echo "✅ 验证恢复..."
sleep 5
if systemctl is-active --quiet daily-word; then
    echo "✅ 恢复成功，服务正常运行"
    echo "📁 当前系统备份保存在: $CURRENT_BACKUP"
else
    echo "❌ 恢复失败，回滚到原系统"
    rm -rf "$HOME/daily-word-epaper"
    mv "$CURRENT_BACKUP" "$HOME/daily-word-epaper"
    sudo systemctl start daily-word
fi

# 清理临时文件
rm -rf "$RESTORE_DIR"

echo "=== 恢复完成 ==="
EOF

chmod +x scripts/restore.sh
```

## 📊 性能监控

### 系统监控

#### 创建监控仪表板

```bash
# 创建监控仪表板脚本
cat > scripts/dashboard.py << 'EOF'
#!/usr/bin/env python3
"""
系统监控仪表板
实时显示系统状态和性能指标
"""

import time
import json
import psutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

class SystemMonitor:
    def __init__(self):
        self.data_file = Path('data/metrics.json')
        
    def get_system_metrics(self):
        """获取系统指标"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'temperature': self.get_cpu_temperature(),
            'uptime': time.time() - psutil.boot_time(),
            'load_avg': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
            'service_status': self.check_service_status()
        }
    
    def get_cpu_temperature(self):
        """获取CPU温度"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000.0
                return temp
        except:
            return None
    
    def check_service_status(self):
        """检查服务状态"""
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'daily-word'],
                capture_output=True, text=True
            )
            return result.stdout.strip() == 'active'
        except:
            return False
    
    def get_historical_data(self, hours=24):
        """获取历史数据"""
        if not self.data_file.exists():
            return []
        
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        # 过滤最近N小时的数据
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered_data = []
        
        for record in data:
            try:
                record_time = datetime.fromisoformat(record['timestamp'])
                if record_time >= cutoff_time:
                    filtered_data.append(record)
            except:
                continue
        
        return filtered_data
    
    def display_dashboard(self):
        """显示监控仪表板"""
        # 清屏
        print('\033[2J\033[H')
        
        # 获取当前指标
        current = self.get_system_metrics()
        historical = self.get_historical_data()
        
        print("=" * 60)
        print(f"📊 每日单词系统监控仪表板 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 系统状态
        print("\n🖥️ 系统状态:")
        print(f"  CPU使用率: {current['cpu_percent']:6.1f}%")
        print(f"  内存使用率: {current['memory_percent']:6.1f}%")
        print(f"  磁盘使用率: {current['disk_percent']:6.1f}%")
        
        if current['temperature']:
            temp_status = "🔥" if current['temperature'] > 70 else "🌡️"
            print(f"  CPU温度: {temp_status} {current['temperature']:6.1f}°C")
        
        uptime_hours = current['uptime'] / 3600
        print(f"  系统运行时间: {uptime_hours:6.1f} 小时")
        
        # 服务状态
        service_icon = "✅" if current['service_status'] else "❌"
        service_text = "运行中" if current['service_status'] else "已停止"
        print(f"\n🔧 服务状态:")
        print(f"  daily-word服务: {service_icon} {service_text}")
        
        # 历史趋势
        if len(historical) > 1:
            print(f"\n📈 24小时趋势 (基于{len(historical)}个数据点):")
            
            cpu_values = [h['cpu_percent'] for h in historical if 'cpu_percent' in h]
            memory_values = [h['memory_percent'] for h in historical if 'memory_percent' in h]
            
            if cpu_values:
                print(f"  CPU: 平均 {sum(cpu_values)/len(cpu_values):5.1f}% | "
                      f"最高 {max(cpu_values):5.1f}% | 最低 {min(cpu_values):5.1f}%")
            
            if memory_values:
                print(f"  内存: 平均 {sum(memory_values)/len(memory_values):5.1f}% | "
                      f"最高 {max(memory_values):5.1f}% | 最低 {min(memory_values):5.1f}%")
        
        # 磁盘空间详情
        print(f"\n💾 磁盘空间详情:")
        disk_usage = psutil.disk_usage('/')
        total_gb = disk_usage.total / (1024**3)
        used_gb = disk_usage.used / (1024**3)
        free_gb = disk_usage.free / (1024**3)
        
        print(f"  总容量: {total_gb:6.1f} GB")
        print(f"  已使用: {used_gb:6.1f} GB")
        print(f"  可用空间: {free_gb:6.1f} GB")
        
        # 最近日志
        print(f"\n📝 最近日志 (最后5条):")
        try:
            log_file = Path('data/daily_word.log')
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:
                        print(f"  {line.strip()}")
            else:
                print("  暂无日志文件")
        except Exception as e:
            print(f"  读取日志失败: {e}")
        
        print("\n" + "=" * 60)
        print("按 Ctrl+C 退出监控")
        
    def run_continuous_monitor(self, interval=30):
        """持续监控模式"""
        try:
            while True:
                self.display_dashboard()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n👋 监控已停止")

def main():
    """主函数"""
    import sys
    
    monitor = SystemMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        monitor.run_continuous_monitor()
    else:
        monitor.display_dashboard()

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/dashboard.py
```

#### 运行监控仪表板

```bash
# 查看当前状态
python3 scripts/dashboard.py

# 持续监控模式
python3 scripts/dashboard.py --continuous

# 添加到系统命令
echo 'alias monitor="cd ~/daily-word-epaper && python3 scripts/dashboard.py"' >> ~/.bashrc
source ~/.bashrc
```

### 性能优化

#### 系统优化脚本

```bash
# 创建性能优化脚本
cat > scripts/optimize.sh << 'EOF'
#!/bin/bash
# 系统性能优化脚本

echo "=== 开始系统优化 $(date) ==="

# 1. 内存优化
echo "🧠 优化内存使用..."
# 清理页面缓存
sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
echo "  ✅ 清理系统缓存完成"

# 2. 磁盘优化
echo "💾 优化磁盘性能..."
# 清理临时文件
sudo find /tmp -type f -atime +7 -delete 2>/dev/null
sudo find /var/tmp -type f -atime +7 -delete 2>/dev/null
echo "  ✅ 清理临时文件完成"

# 清理日志文件
sudo journalctl --vacuum-time=7d
echo "  ✅ 清理系统日志完成"

# 3. 网络优化
echo "🌐 优化网络设置..."
# 优化TCP设置（仅在需要时）
if ! grep -q "net.core.rmem_max" /etc/sysctl.conf; then
    echo "net.core.rmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
    echo "net.core.wmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
    echo "  ✅ 网络参数优化完成"
fi

# 4. 服务优化
echo "🔧 优化服务配置..."
# 重启服务以应用优化
sudo systemctl restart daily-word
echo "  ✅ 服务重启完成"

# 5. 显示优化结果
echo "📊 优化结果:"
free -h | head -2
df -h / | tail -1

echo "=== 系统优化完成 ==="
EOF

chmod +x scripts/optimize.sh
```

## 🚨 告警系统

### 创建告警脚本

```bash
# 创建告警系统
cat > scripts/alert.py << 'EOF'
#!/usr/bin/env python3
"""
系统告警脚本
监控系统状态并发送告警通知
"""

import json
import smtplib
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertSystem:
    def __init__(self):
        self.config_file = Path('data/alert_config.json')
        self.alert_log = Path('logs/alerts.log')
        self.load_config()
    
    def load_config(self):
        """加载告警配置"""
        default_config = {
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'to_email': ''
            },
            'thresholds': {
                'cpu_percent': 90,
                'memory_percent': 90,
                'disk_percent': 90,
                'temperature': 80,
                'error_count': 10
            },
            'check_interval': 300  # 5分钟
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """保存告警配置"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_system_health(self):
        """检查系统健康状态"""
        alerts = []
        
        # CPU检查
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > self.config['thresholds']['cpu_percent']:
            alerts.append(f"CPU使用率过高: {cpu_percent:.1f}%")
        
        # 内存检查
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > self.config['thresholds']['memory_percent']:
            alerts.append(f"内存使用率过高: {memory_percent:.1f}%")
        
        # 磁盘检查
        disk_percent = psutil.disk_usage('/').percent
        if disk_percent > self.config['thresholds']['disk_percent']:
            alerts.append(f"磁盘使用率过高: {disk_percent:.1f}%")
        
        # 温度检查
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000.0
                if temp > self.config['thresholds']['temperature']:
                    alerts.append(f"CPU温度过高: {temp:.1f}°C")
        except:
            pass
        
        # 服务状态检查
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'daily-word'],
                capture_output=True, text=True
            )
            if result.stdout.strip() != 'active':
                alerts.append("daily-word服务未运行")
        except:
            alerts.append("无法检查服务状态")
        
        # 错误日志检查
        try:
            log_file = Path('data/daily_word.log')
            if log_file.exists():
                with open(log_file, 'r') as f:
                    content = f.read()
                    error_count = content.count('ERROR')
                    if error_count > self.config['thresholds']['error_count']:
                        alerts.append(f"错误日志过多: {error_count}条")
        except:
            pass
        
        return alerts
    
    def send_email_alert(self, subject, message):
        """发送邮件告警"""
        if not self.config['email']['enabled']:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = self.config['email']['to_email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(
                self.config['email']['smtp_server'],
                self.config['email']['smtp_port']
            )
            server.starttls()
            server.login(
                self.config['email']['username'],
                self.config['email']['password']
            )
            
            text = msg.as_string()
            server.sendmail(
                self.config['email']['username'],
                self.config['email']['to_email'],
                text
            )
            server.quit()
            
            return True
        except Exception as e:
            self.log_alert(f"邮件发送失败: {e}")
            return False
    
    def log_alert(self, message):
        """记录告警日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        
        with open(self.alert_log, 'a') as f:
            f.write(log_message)
        
        print(log_message.strip())
    
    def run_check(self):
        """运行一次检查"""
        alerts = self.check_system_health()
        
        if alerts:
            alert_message = "检测到以下问题:\n\n" + "\n".join(f"• {alert}" for alert in alerts)
            alert_message += f"\n\n检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 记录告警
            self.log_alert(f"发现 {len(alerts)} 个告警")
            
            # 发送邮件
            if self.send_email_alert("每日单词系统告警", alert_message):
                self.log_alert("告警邮件发送成功")
            
            return True
        else:
            return False

def main():
    """主函数"""
    alert_system = AlertSystem()
    has_alerts = alert_system.run_check()
    
    if not has_alerts:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 系统状态正常")

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/alert.py

# 添加到cron（每5分钟检查一次）
echo "*/5 * * * * cd $HOME/daily-word-epaper && python3 scripts/alert.py >> logs/alert_check.log 2>&1" | crontab -
```

## 🔄 自动化维护

### 创建自动维护脚本

```bash
# 创建自动维护脚本
cat > scripts/auto_maintenance.sh << 'EOF'
#!/bin/bash
# 自动维护脚本 - 每周执行

echo "=== 开始自动维护 $(date) ==="

# 1. 系统健康检查
echo "🔍 执行系统健康检查..."
./scripts/daily_check.sh

# 2. 清理日志
echo "🧹 清理旧日志..."
./scripts/cleanup_logs.sh

# 3. 系统优化
echo "⚡ 执行系统优化..."
./scripts/optimize.sh

# 4. 备份系统
echo "💾 执行系统备份..."
./scripts/backup.sh

# 5. 更新系统（可选）
if [ "$1" = "--update" ]; then
    echo "📦 更新系统软件..."
    ./scripts/system_update.sh
fi

# 6. 重启服务
echo "🔄 重启服务..."
sudo systemctl restart daily-word

# 7. 验证服务状态
echo "✅ 验证服务状态..."
sleep 10
if systemctl is-active --quiet daily-word; then
    echo "✅ 维护完成，服务正常运行"
else
    echo "❌ 维护完成，但服务异常"
fi

echo "=== 自动维护完成 ==="
EOF

chmod +x scripts/auto_maintenance.sh

# 添加到cron（每周日凌晨1点执行）
echo "0 1 * * 0 cd $HOME/daily-word-epaper && ./scripts/auto_maintenance.sh >> logs/maintenance.log 2>&1" | crontab -
```

## 📋 维护检查清单

### 每日检查项目
- [ ] 服务运行状态
- [ ] 系统资源使用
- [ ] 错误日志数量
- [ ] 网络连接状态
- [ ] 墨水屏显示正常

### 每周检查项目
- [ ] 磁盘空间使用
- [ ] 日志文件大小
- [ ] 系统更新状态
- [ ] 备份文件完整性
- [ ] 性能指标趋势

### 每月检查项目
- [ ] 系统安全更新
- [ ] 配置文件备份
- [ ] 硬件状态检查
- [ ] 长期性能分析
- [ ] 容量规划评估

---

**下一步：** [故障排除](07-troubleshooting.md)