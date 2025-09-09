# 故障排除

## 📋 概述

本章节提供常见问题的诊断方法和解决方案，帮助您快速定位和解决系统运行中遇到的各种问题。

## 🔧 快速诊断工具

### 系统诊断脚本

```bash
# 创建快速诊断脚本
cat > scripts/diagnose.py << 'EOF'
#!/usr/bin/env python3
"""
系统快速诊断工具
自动检测和诊断常见问题
"""

import os
import sys
import json
import psutil
import subprocess
from pathlib import Path
from datetime import datetime

class SystemDiagnostic:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.info = []
    
    def add_issue(self, message):
        """添加问题"""
        self.issues.append(f"❌ {message}")
    
    def add_warning(self, message):
        """添加警告"""
        self.warnings.append(f"⚠️ {message}")
    
    def add_info(self, message):
        """添加信息"""
        self.info.append(f"ℹ️ {message}")
    
    def check_environment(self):
        """检查运行环境"""
        print("🔍 检查运行环境...")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
            self.add_issue(f"Python版本过低: {python_version.major}.{python_version.minor}")
        else:
            self.add_info(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查虚拟环境
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self.add_info("虚拟环境: 已激活")
        else:
            self.add_warning("虚拟环境: 未激活")
        
        # 检查必要的目录
        required_dirs = ['src', 'data', 'logs', 'scripts']
        for dir_name in required_dirs:
            if Path(dir_name).exists():
                self.add_info(f"目录 {dir_name}: 存在")
            else:
                self.add_issue(f"目录 {dir_name}: 不存在")
        
        # 检查必要的文件
        required_files = [
            'src/daily_word_rpi.py',
            'src/class_word_api.py',
            'src/epaper_display_rpi.py',
            'src/word_config.py'
        ]
        for file_path in required_files:
            if Path(file_path).exists():
                self.add_info(f"文件 {file_path}: 存在")
            else:
                self.add_issue(f"文件 {file_path}: 不存在")
    
    def check_dependencies(self):
        """检查依赖包"""
        print("📦 检查依赖包...")
        
        required_packages = [
            'requests', 'Pillow', 'RPi.GPIO', 'spidev', 'psutil'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_').lower())
                self.add_info(f"依赖包 {package}: 已安装")
            except ImportError:
                self.add_issue(f"依赖包 {package}: 未安装")
    
    def check_hardware(self):
        """检查硬件状态"""
        print("🔌 检查硬件状态...")
        
        # 检查GPIO
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.cleanup()
            self.add_info("GPIO: 可用")
        except Exception as e:
            self.add_issue(f"GPIO: 不可用 - {e}")
        
        # 检查SPI
        try:
            import spidev
            spi = spidev.SpiDev()
            spi.open(0, 0)
            spi.close()
            self.add_info("SPI: 可用")
        except Exception as e:
            self.add_issue(f"SPI: 不可用 - {e}")
        
        # 检查I2C（如果需要）
        if Path('/dev/i2c-1').exists():
            self.add_info("I2C: 设备存在")
        else:
            self.add_warning("I2C: 设备不存在")
    
    def check_services(self):
        """检查服务状态"""
        print("🔧 检查服务状态...")
        
        # 检查systemd服务
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'daily-word'],
                capture_output=True, text=True
            )
            if result.stdout.strip() == 'active':
                self.add_info("daily-word服务: 运行中")
            else:
                self.add_issue("daily-word服务: 未运行")
        except Exception as e:
            self.add_warning(f"无法检查服务状态: {e}")
        
        # 检查服务文件
        service_file = Path('/etc/systemd/system/daily-word.service')
        if service_file.exists():
            self.add_info("服务文件: 存在")
        else:
            self.add_issue("服务文件: 不存在")
    
    def check_network(self):
        """检查网络连接"""
        print("🌐 检查网络连接...")
        
        # 检查基本网络连接
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.add_info("网络连接: 正常")
        except Exception:
            self.add_issue("网络连接: 异常")
        
        # 检查API连接
        try:
            import requests
            response = requests.get("https://api.quotable.io/random", timeout=5)
            if response.status_code == 200:
                self.add_info("API连接: 正常")
            else:
                self.add_warning(f"API连接: 状态码 {response.status_code}")
        except Exception as e:
            self.add_warning(f"API连接: 异常 - {e}")
    
    def check_logs(self):
        """检查日志文件"""
        print("📝 检查日志文件...")
        
        log_files = [
            'data/daily_word.log',
            'logs/cron.log',
            'logs/error.log'
        ]
        
        for log_file in log_files:
            log_path = Path(log_file)
            if log_path.exists():
                # 检查文件大小
                size_mb = log_path.stat().st_size / (1024 * 1024)
                if size_mb > 100:
                    self.add_warning(f"日志文件 {log_file}: 过大 ({size_mb:.1f}MB)")
                else:
                    self.add_info(f"日志文件 {log_file}: 正常 ({size_mb:.1f}MB)")
                
                # 检查最近错误
                try:
                    with open(log_path, 'r') as f:
                        content = f.read()
                        error_count = content.count('ERROR')
                        if error_count > 10:
                            self.add_warning(f"日志文件 {log_file}: 错误过多 ({error_count}个)")
                except Exception:
                    pass
            else:
                self.add_warning(f"日志文件 {log_file}: 不存在")
    
    def check_system_resources(self):
        """检查系统资源"""
        print("💻 检查系统资源...")
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            self.add_issue(f"CPU使用率过高: {cpu_percent:.1f}%")
        elif cpu_percent > 70:
            self.add_warning(f"CPU使用率较高: {cpu_percent:.1f}%")
        else:
            self.add_info(f"CPU使用率: {cpu_percent:.1f}%")
        
        # 内存使用率
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            self.add_issue(f"内存使用率过高: {memory.percent:.1f}%")
        elif memory.percent > 80:
            self.add_warning(f"内存使用率较高: {memory.percent:.1f}%")
        else:
            self.add_info(f"内存使用率: {memory.percent:.1f}%")
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > 90:
            self.add_issue(f"磁盘使用率过高: {disk_percent:.1f}%")
        elif disk_percent > 80:
            self.add_warning(f"磁盘使用率较高: {disk_percent:.1f}%")
        else:
            self.add_info(f"磁盘使用率: {disk_percent:.1f}%")
        
        # CPU温度
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000.0
                if temp > 80:
                    self.add_issue(f"CPU温度过高: {temp:.1f}°C")
                elif temp > 70:
                    self.add_warning(f"CPU温度较高: {temp:.1f}°C")
                else:
                    self.add_info(f"CPU温度: {temp:.1f}°C")
        except Exception:
            self.add_warning("无法读取CPU温度")
    
    def run_full_diagnostic(self):
        """运行完整诊断"""
        print("=" * 60)
        print(f"🔍 系统诊断报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        self.check_environment()
        self.check_dependencies()
        self.check_hardware()
        self.check_services()
        self.check_network()
        self.check_logs()
        self.check_system_resources()
        
        # 输出结果
        print("\n" + "=" * 60)
        print("📊 诊断结果汇总")
        print("=" * 60)
        
        if self.issues:
            print(f"\n🚨 发现 {len(self.issues)} 个问题:")
            for issue in self.issues:
                print(f"  {issue}")
        
        if self.warnings:
            print(f"\n⚠️ 发现 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.info:
            print(f"\n✅ 正常项目 ({len(self.info)} 个):")
            for info in self.info[:5]:  # 只显示前5个
                print(f"  {info}")
            if len(self.info) > 5:
                print(f"  ... 还有 {len(self.info) - 5} 个正常项目")
        
        # 总体评估
        print(f"\n📋 总体评估:")
        if not self.issues:
            if not self.warnings:
                print("  🎉 系统状态优秀，无问题无警告")
            else:
                print("  👍 系统状态良好，有少量警告")
        else:
            print("  ⚠️ 系统存在问题，需要处理")
        
        print("\n" + "=" * 60)
        
        return len(self.issues) == 0

def main():
    """主函数"""
    diagnostic = SystemDiagnostic()
    success = diagnostic.run_full_diagnostic()
    
    if not success:
        print("\n💡 建议:")
        print("  1. 查看上述问题列表")
        print("  2. 参考故障排除文档")
        print("  3. 运行相应的修复脚本")
        print("  4. 如需帮助，请查看日志文件")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x scripts/diagnose.py
```

## 🚨 常见问题及解决方案

### 1. 服务启动问题

#### 问题：服务无法启动

**症状：**
```bash
sudo systemctl start daily-word
# 输出: Job for daily-word.service failed
```

**诊断步骤：**
```bash
# 1. 查看服务状态
sudo systemctl status daily-word

# 2. 查看详细日志
sudo journalctl -u daily-word -n 50

# 3. 检查配置文件
cat /etc/systemd/system/daily-word.service

# 4. 测试手动运行
cd ~/daily-word-epaper
source venv/bin/activate
python3 src/daily_word_rpi.py --test
```

**解决方案：**

**方案1：权限问题**
```bash
# 修复文件权限
chmod +x ~/daily-word-epaper/src/*.py
chown -R $USER:$USER ~/daily-word-epaper/

# 重新创建服务文件
sudo systemctl stop daily-word
sudo rm /etc/systemd/system/daily-word.service
# 重新运行安装脚本
```

**方案2：路径问题**
```bash
# 检查服务文件中的路径
sudo nano /etc/systemd/system/daily-word.service

# 确保路径正确：
# WorkingDirectory=/home/pi/daily-word-epaper
# ExecStart=/home/pi/daily-word-epaper/venv/bin/python ...
```

**方案3：依赖问题**
```bash
# 重新安装依赖
cd ~/daily-word-epaper
source venv/bin/activate
pip install -r requirements.txt
```

#### 问题：服务频繁重启

**症状：**
```bash
sudo systemctl status daily-word
# 显示: Active: activating (auto-restart)
```

**解决方案：**
```bash
# 1. 增加重启间隔
sudo nano /etc/systemd/system/daily-word.service
# 修改: RestartSec=60

# 2. 检查内存泄漏
python3 scripts/monitor.py

# 3. 添加资源限制
# 在服务文件中添加:
# MemoryMax=512M
# CPUQuota=80%
```

### 2. 墨水屏显示问题

#### 问题：墨水屏无显示

**症状：**
- 程序运行正常但屏幕无内容
- 屏幕显示异常图案

**诊断步骤：**
```bash
# 1. 检查硬件连接
python3 -c "
import RPi.GPIO as GPIO
import spidev
try:
    GPIO.setmode(GPIO.BCM)
    spi = spidev.SpiDev()
    spi.open(0, 0)
    print('✅ 硬件连接正常')
    spi.close()
    GPIO.cleanup()
except Exception as e:
    print(f'❌ 硬件连接异常: {e}')
"

# 2. 检查SPI是否启用
ls /dev/spi*
# 应该看到 /dev/spidev0.0

# 3. 测试墨水屏初始化
python3 -c "
from src.epaper_display_rpi import EPaperDisplay
display = EPaperDisplay()
print('墨水屏初始化:', '成功' if display.epd else '失败')
"
```

**解决方案：**

**方案1：启用SPI**
```bash
# 启用SPI接口
sudo raspi-config
# 选择: Interfacing Options -> SPI -> Yes

# 或直接修改配置
echo 'dtparam=spi=on' | sudo tee -a /boot/config.txt
sudo reboot
```

**方案2：检查接线**
```bash
# 创建接线检查脚本
cat > scripts/check_wiring.py << 'EOF'
#!/usr/bin/env python3
"""检查墨水屏接线"""

import RPi.GPIO as GPIO
import time

# 标准接线定义
PINS = {
    'VCC': '3.3V',
    'GND': 'GND', 
    'DIN': 'GPIO10 (MOSI)',
    'CLK': 'GPIO11 (SCLK)',
    'CS': 'GPIO8 (CE0)',
    'DC': 'GPIO25',
    'RST': 'GPIO17',
    'BUSY': 'GPIO24'
}

print("📌 标准接线图:")
for signal, pin in PINS.items():
    print(f"  {signal:4} -> {pin}")

print("\n🔍 GPIO状态检查:")
GPIO.setmode(GPIO.BCM)

test_pins = [17, 24, 25]  # RST, BUSY, DC
for pin in test_pins:
    try:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(pin, GPIO.LOW)
        print(f"  GPIO{pin}: ✅ 正常")
    except Exception as e:
        print(f"  GPIO{pin}: ❌ 异常 - {e}")

GPIO.cleanup()
EOF

python3 scripts/check_wiring.py
```

**方案3：更新驱动**
```bash
# 重新安装墨水屏库
cd ~/daily-word-epaper
source venv/bin/activate
pip uninstall waveshare-epd -y
pip install waveshare-epd
```

#### 问题：显示内容异常

**症状：**
- 文字重叠或错位
- 字体显示不正确
- 图像失真

**解决方案：**
```bash
# 1. 重置显示配置
python3 -c "
from src.epaper_display_rpi import EPaperDisplay
display = EPaperDisplay()
display.clear_display()
print('显示已清空')
"

# 2. 检查字体文件
ls -la /usr/share/fonts/truetype/dejavu/
# 确保字体文件存在

# 3. 调整显示参数
nano src/word_config.py
# 修改字体大小和布局参数
```

### 3. 网络连接问题

#### 问题：API请求失败

**症状：**
```
ERROR - 获取每日单词时出错: HTTPSConnectionPool...
```

**诊断步骤：**
```bash
# 1. 测试基本网络连接
ping -c 4 8.8.8.8

# 2. 测试DNS解析
nslookup api.quotable.io

# 3. 测试API连接
curl -I https://api.quotable.io/random

# 4. 检查防火墙
sudo ufw status
```

**解决方案：**

**方案1：网络配置**
```bash
# 重启网络服务
sudo systemctl restart networking

# 检查网络配置
cat /etc/dhcpcd.conf

# 重新配置WiFi（如果使用WiFi）
sudo raspi-config
# 选择: Network Options -> Wi-fi
```

**方案2：DNS配置**
```bash
# 配置DNS服务器
echo 'nameserver 8.8.8.8' | sudo tee -a /etc/resolv.conf
echo 'nameserver 8.8.4.4' | sudo tee -a /etc/resolv.conf
```

**方案3：使用本地内容**
```bash
# 修改配置使用本地备用内容
nano src/word_config.py
# 设置: USE_LOCAL_FALLBACK = True
```

### 4. 内存和性能问题

#### 问题：内存不足

**症状：**
```
MemoryError: Unable to allocate array
```

**解决方案：**
```bash
# 1. 增加交换空间
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# 修改: CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# 2. 优化内存使用
python3 scripts/optimize.sh

# 3. 限制服务内存使用
sudo nano /etc/systemd/system/daily-word.service
# 添加: MemoryMax=256M
```

#### 问题：CPU使用率过高

**解决方案：**
```bash
# 1. 检查进程
top -p $(pgrep -f daily_word)

# 2. 优化更新频率
nano src/word_config.py
# 增加: UPDATE_INTERVAL = 3600  # 1小时更新一次

# 3. 限制CPU使用
sudo nano /etc/systemd/system/daily-word.service
# 添加: CPUQuota=50%
```

### 5. 权限问题

#### 问题：GPIO权限不足

**症状：**
```
RuntimeError: No access to /dev/mem
```

**解决方案：**
```bash
# 1. 添加用户到gpio组
sudo usermod -a -G gpio $USER

# 2. 添加用户到spi组
sudo usermod -a -G spi $USER

# 3. 重新登录或重启
sudo reboot

# 4. 检查权限
groups $USER
# 应该包含: gpio spi
```

#### 问题：文件权限错误

**解决方案：**
```bash
# 修复所有文件权限
cd ~/daily-word-epaper
find . -type f -name "*.py" -exec chmod +x {} \;
find . -type f -name "*.sh" -exec chmod +x {} \;
chown -R $USER:$USER .
```

## 🛠️ 修复工具

### 自动修复脚本

```bash
# 创建自动修复脚本
cat > scripts/auto_fix.py << 'EOF'
#!/usr/bin/env python3
"""
自动修复脚本
尝试自动修复常见问题
"""

import os
import sys
import subprocess
from pathlib import Path

class AutoFix:
    def __init__(self):
        self.fixes_applied = []
        self.fixes_failed = []
    
    def run_command(self, command, description):
        """运行命令并记录结果"""
        try:
            result = subprocess.run(
                command, shell=True, 
                capture_output=True, text=True
            )
            if result.returncode == 0:
                self.fixes_applied.append(description)
                return True
            else:
                self.fixes_failed.append(f"{description}: {result.stderr}")
                return False
        except Exception as e:
            self.fixes_failed.append(f"{description}: {e}")
            return False
    
    def fix_permissions(self):
        """修复权限问题"""
        print("🔧 修复权限问题...")
        
        commands = [
            ("find . -type f -name '*.py' -exec chmod +x {} \\;", "Python文件权限"),
            ("find . -type f -name '*.sh' -exec chmod +x {} \\;", "Shell脚本权限"),
            (f"chown -R {os.getenv('USER')}:{os.getenv('USER')} .", "文件所有权"),
        ]
        
        for command, description in commands:
            self.run_command(command, description)
    
    def fix_dependencies(self):
        """修复依赖问题"""
        print("📦 修复依赖问题...")
        
        # 激活虚拟环境并重新安装依赖
        commands = [
            ("source venv/bin/activate && pip install --upgrade pip", "升级pip"),
            ("source venv/bin/activate && pip install -r requirements.txt", "安装依赖"),
        ]
        
        for command, description in commands:
            self.run_command(command, description)
    
    def fix_service(self):
        """修复服务问题"""
        print("🔧 修复服务问题...")
        
        commands = [
            ("sudo systemctl daemon-reload", "重新加载systemd"),
            ("sudo systemctl stop daily-word", "停止服务"),
            ("sudo systemctl start daily-word", "启动服务"),
        ]
        
        for command, description in commands:
            self.run_command(command, description)
    
    def fix_logs(self):
        """修复日志问题"""
        print("📝 修复日志问题...")
        
        # 创建必要的目录
        Path('logs').mkdir(exist_ok=True)
        Path('data').mkdir(exist_ok=True)
        
        # 清理大日志文件
        commands = [
            ("find logs/ -name '*.log' -size +100M -exec truncate -s 0 {} \\;", "清理大日志文件"),
            ("find data/ -name '*.log' -size +100M -exec truncate -s 0 {} \\;", "清理大数据文件"),
        ]
        
        for command, description in commands:
            self.run_command(command, description)
    
    def run_all_fixes(self):
        """运行所有修复"""
        print("=" * 50)
        print("🔧 自动修复工具")
        print("=" * 50)
        
        self.fix_permissions()
        self.fix_dependencies()
        self.fix_logs()
        self.fix_service()
        
        # 输出结果
        print("\n" + "=" * 50)
        print("📊 修复结果")
        print("=" * 50)
        
        if self.fixes_applied:
            print(f"\n✅ 成功修复 ({len(self.fixes_applied)} 项):")
            for fix in self.fixes_applied:
                print(f"  • {fix}")
        
        if self.fixes_failed:
            print(f"\n❌ 修复失败 ({len(self.fixes_failed)} 项):")
            for fix in self.fixes_failed:
                print(f"  • {fix}")
        
        if not self.fixes_failed:
            print("\n🎉 所有修复都已成功完成！")
        else:
            print("\n⚠️ 部分修复失败，可能需要手动处理")

def main():
    """主函数"""
    fixer = AutoFix()
    fixer.run_all_fixes()

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/auto_fix.py
```

### 系统重置脚本

```bash
# 创建系统重置脚本
cat > scripts/reset_system.sh << 'EOF'
#!/bin/bash
# 系统重置脚本 - 谨慎使用

echo "⚠️ 警告: 此操作将重置整个系统到初始状态"
echo "这将删除所有数据和日志文件"
read -p "确定要继续吗? (输入 'RESET' 确认): " confirm

if [ "$confirm" != "RESET" ]; then
    echo "操作已取消"
    exit 1
fi

echo "=== 开始系统重置 $(date) ==="

# 1. 停止服务
echo "⏹️ 停止服务..."
sudo systemctl stop daily-word 2>/dev/null || true
sudo systemctl disable daily-word 2>/dev/null || true

# 2. 备份配置
echo "💾 备份配置..."
mkdir -p ~/daily-word-backup-$(date +%Y%m%d)
cp src/word_config.py ~/daily-word-backup-$(date +%Y%m%d)/ 2>/dev/null || true

# 3. 清理数据
echo "🧹 清理数据..."
rm -rf data/*.log data/*.json data/*.txt
rm -rf logs/*.log

# 4. 重新创建目录
echo "📁 重新创建目录..."
mkdir -p data logs scripts

# 5. 重新安装依赖
echo "📦 重新安装依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 6. 重新配置服务
echo "🔧 重新配置服务..."
sudo systemctl daemon-reload
sudo systemctl enable daily-word
sudo systemctl start daily-word

# 7. 验证重置
echo "✅ 验证重置..."
sleep 5
if systemctl is-active --quiet daily-word; then
    echo "✅ 系统重置成功"
else
    echo "❌ 系统重置失败"
fi

echo "=== 系统重置完成 ==="
EOF

chmod +x scripts/reset_system.sh
```

## 📞 获取帮助

### 日志收集脚本

```bash
# 创建日志收集脚本
cat > scripts/collect_logs.sh << 'EOF'
#!/bin/bash
# 日志收集脚本 - 用于技术支持

SUPPORT_DIR="support-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SUPPORT_DIR"

echo "📋 收集系统信息用于技术支持..."

# 1. 系统信息
echo "🖥️ 收集系统信息..."
uname -a > "$SUPPORT_DIR/system_info.txt"
cat /proc/cpuinfo > "$SUPPORT_DIR/cpu_info.txt"
free -h > "$SUPPORT_DIR/memory_info.txt"
df -h > "$SUPPORT_DIR/disk_info.txt"

# 2. 服务状态
echo "🔧 收集服务状态..."
systemctl status daily-word > "$SUPPORT_DIR/service_status.txt" 2>&1
journalctl -u daily-word -n 100 > "$SUPPORT_DIR/service_logs.txt" 2>&1

# 3. 应用日志
echo "📝 收集应用日志..."
cp data/*.log "$SUPPORT_DIR/" 2>/dev/null || true
cp logs/*.log "$SUPPORT_DIR/" 2>/dev/null || true

# 4. 配置文件
echo "⚙️ 收集配置文件..."
cp src/word_config.py "$SUPPORT_DIR/" 2>/dev/null || true
cp /etc/systemd/system/daily-word.service "$SUPPORT_DIR/" 2>/dev/null || true

# 5. 网络测试
echo "🌐 执行网络测试..."
ping -c 4 8.8.8.8 > "$SUPPORT_DIR/network_test.txt" 2>&1
curl -I https://api.quotable.io/random > "$SUPPORT_DIR/api_test.txt" 2>&1

# 6. 硬件测试
echo "🔌 执行硬件测试..."
python3 scripts/diagnose.py > "$SUPPORT_DIR/diagnostic_report.txt" 2>&1

# 7. 打包
echo "📦 打包支持文件..."
tar -czf "${SUPPORT_DIR}.tar.gz" "$SUPPORT_DIR"
rm -rf "$SUPPORT_DIR"

echo "✅ 支持文件已收集: ${SUPPORT_DIR}.tar.gz"
echo "请将此文件发送给技术支持团队"
EOF

chmod +x scripts/collect_logs.sh
```

### 联系方式

如果遇到无法解决的问题，请：

1. **运行诊断工具**
   ```bash
   python3 scripts/diagnose.py
   ```

2. **收集支持信息**
   ```bash
   ./scripts/collect_logs.sh
   ```

3. **查看文档**
   - 检查本故障排除指南
   - 查看API文档
   - 参考用户手册

4. **社区支持**
   - GitHub Issues
   - 技术论坛
   - 用户群组

## 📋 故障排除检查清单

### 基础检查
- [ ] 运行系统诊断工具
- [ ] 检查服务状态
- [ ] 查看最近日志
- [ ] 验证网络连接
- [ ] 确认硬件连接

### 深入诊断
- [ ] 检查系统资源使用
- [ ] 验证依赖包完整性
- [ ] 测试API连接
- [ ] 检查权限设置
- [ ] 分析错误模式

### 修复尝试
- [ ] 运行自动修复脚本
- [ ] 重启相关服务
- [ ] 清理临时文件
- [ ] 更新依赖包
- [ ] 恢复备份配置

### 最后手段
- [ ] 系统重置
- [ ] 重新安装
- [ ] 联系技术支持
- [ ] 查看社区资源

---

**完成！** 您已完成故障排除指南的学习。