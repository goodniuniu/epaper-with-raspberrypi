# 每日单词墨水屏系统快速修复指南

## 🚨 紧急故障快速修复

### 问题1: 墨水屏无显示 (最常见)

**症状**: 系统运行正常，但墨水屏没有任何显示

**快速诊断**:
```bash
# 1分钟快速检查
daily-word test | grep "显示控制器测试"
```

**快速修复** (5分钟内解决):
```bash
# Step 1: 停止服务
daily-word stop

# Step 2: 检查驱动文件
ls /opt/daily-word-epaper/src/waveshare_epd/epd3in52.py
# 如果文件不存在，执行下面的修复命令

# Step 3: 快速修复驱动 (如果用户有工作的墨水屏代码)
if [ -f ~/Downloads/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd3in52.py ]; then
    cp -r ~/Downloads/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd /opt/daily-word-epaper/src/
    cp ~/Downloads/e-Paper/RaspberryPi_JetsonNano/python/pic/Font.ttc /opt/daily-word-epaper/pic/
    echo "✅ 驱动修复完成"
else
    echo "❌ 需要手动安装waveshare驱动"
fi

# Step 4: 重启服务
daily-word start

# Step 5: 验证修复
daily-word update
```

---

### 问题2: 服务无法启动

**症状**: `daily-word start` 失败

**快速诊断**:
```bash
# 检查错误信息
daily-word logs | tail -10
```

**快速修复**:
```bash
# 常见原因1: 权限问题
sudo chown -R admin:admin /opt/daily-word-epaper/
sudo chmod +x /opt/daily-word-epaper/src/daily_word_main.py

# 常见原因2: Python依赖缺失
cd /opt/daily-word-epaper && ./venv/bin/pip install gpiozero RPi.GPIO spidev

# 常见原因3: 端口占用
sudo pkill -f daily_word
sleep 2
daily-word start
```

---

### 问题3: 显示内容被覆盖

**症状**: 新内容显示后很快被其他内容覆盖

**快速诊断**:
```bash
# 检查冲突进程
ps aux | grep -E "(display_epaper|epd)" | grep -v grep
crontab -l | grep display
```

**快速修复**:
```bash
# 临时停止冲突任务
sudo pkill -f display_epaper

# 永久解决: 注释crontab冲突任务
crontab -l > /tmp/crontab_backup
crontab -l | sed 's/^.*display_epaper.*$/# &/' | crontab -

echo "✅ 冲突任务已注释，原配置已备份到 /tmp/crontab_backup"
```

---

## 🔧 常用修复命令集

### 一键重置服务
```bash
#!/bin/bash
# 保存为 reset_service.sh
daily-word stop
sudo pkill -f daily_word
sleep 3
daily-word start
daily-word status
```

### 一键修复权限
```bash
#!/bin/bash
# 保存为 fix_permissions.sh
sudo chown -R admin:admin /opt/daily-word-epaper/
sudo chmod +x /opt/daily-word-epaper/src/*.py
sudo chmod +x /usr/local/bin/daily-word
echo "✅ 权限修复完成"
```

### 一键检查依赖
```bash
#!/bin/bash
# 保存为 check_deps.sh
echo "检查Python依赖..."
cd /opt/daily-word-epaper
./venv/bin/python -c "
import sys
modules = ['PIL', 'requests', 'RPi.GPIO', 'spidev', 'gpiozero']
missing = []
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module}')
        missing.append(module)

if missing:
    print(f'缺失模块: {missing}')
    print('运行: ./venv/bin/pip install ' + ' '.join(missing))
else:
    print('✅ 所有依赖正常')
"
```

---

## 📋 故障分类快速索引

### A类故障 (硬件相关)
- **A1**: 墨水屏无显示 → [问题1修复方案](#问题1-墨水屏无显示-最常见)
- **A2**: SPI通信错误 → 检查硬件连接
- **A3**: GPIO权限错误 → 运行权限修复脚本

### B类故障 (软件相关)  
- **B1**: 服务启动失败 → [问题2修复方案](#问题2-服务无法启动)
- **B2**: Python模块缺失 → 运行依赖检查脚本
- **B3**: 配置文件错误 → 重新运行安装脚本

### C类故障 (冲突相关)
- **C1**: 显示内容被覆盖 → [问题3修复方案](#问题3-显示内容被覆盖)
- **C2**: 端口占用 → 杀死冲突进程
- **C3**: 多服务冲突 → 检查systemd和crontab

---

## 🚀 5分钟完整诊断流程

```bash
#!/bin/bash
echo "=== 每日单词墨水屏系统诊断 ==="
echo "开始时间: $(date)"
echo

# 1. 基础检查
echo "1. 基础文件检查..."
[ -f /opt/daily-word-epaper/src/daily_word_main.py ] && echo "✅ 主程序" || echo "❌ 主程序缺失"
[ -f /opt/daily-word-epaper/src/daily_word_epaper_controller.py ] && echo "✅ 墨水屏控制器" || echo "❌ 控制器缺失"
[ -d /opt/daily-word-epaper/src/waveshare_epd ] && echo "✅ 驱动库" || echo "❌ 驱动库缺失"
[ -f /opt/daily-word-epaper/pic/Font.ttc ] && echo "✅ 字体文件" || echo "❌ 字体文件缺失"

# 2. 服务状态
echo -e "\n2. 服务状态检查..."
if systemctl is-active --quiet daily-word; then
    echo "✅ 服务运行中"
else
    echo "❌ 服务未运行"
fi

# 3. 进程检查
echo -e "\n3. 进程冲突检查..."
CONFLICTS=$(ps aux | grep -E "(display_epaper|epd)" | grep -v grep | wc -l)
if [ $CONFLICTS -gt 1 ]; then
    echo "⚠️  发现 $CONFLICTS 个可能冲突的进程"
    ps aux | grep -E "(display_epaper|epd)" | grep -v grep
else
    echo "✅ 无进程冲突"
fi

# 4. 快速功能测试
echo -e "\n4. 功能测试..."
timeout 30 daily-word test > /tmp/test_result 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 系统测试通过"
else
    echo "❌ 系统测试失败"
    echo "错误信息:"
    tail -5 /tmp/test_result
fi

echo -e "\n=== 诊断完成 ==="
echo "如需详细故障排查，请查看: docs/troubleshooting/epaper-deployment-troubleshooting.md"
```

---

## 📞 紧急联系流程

### 自助解决 (推荐)
1. 运行5分钟诊断脚本
2. 根据故障分类查找对应解决方案
3. 执行快速修复命令

### 寻求帮助
如果自助解决无效，请收集以下信息:

```bash
# 收集诊断信息
echo "=== 系统信息 ===" > /tmp/debug_info.txt
uname -a >> /tmp/debug_info.txt
echo -e "\n=== 服务状态 ===" >> /tmp/debug_info.txt
daily-word status >> /tmp/debug_info.txt 2>&1
echo -e "\n=== 最近日志 ===" >> /tmp/debug_info.txt
daily-word logs | tail -20 >> /tmp/debug_info.txt
echo -e "\n=== 进程信息 ===" >> /tmp/debug_info.txt
ps aux | grep -E "(daily_word|epd|display)" >> /tmp/debug_info.txt

echo "诊断信息已保存到: /tmp/debug_info.txt"
```

---

**文档版本**: v1.0  
**最后更新**: 2025年9月5日  
**紧急程度**: 🔴 高优先级