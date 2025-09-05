# 每日单词墨水屏系统部署故障排查指南

## 概述

本文档记录了每日单词墨水屏显示系统在树莓派上部署过程中遇到的问题、排查思路和解决方案，为后续部署人员提供参考。

## 部署环境信息

- **硬件平台**: 树莓派 (ARM64架构)
- **操作系统**: Debian GNU/Linux (内核版本: 6.1.63-1+rpt1)
- **墨水屏型号**: Waveshare 3.52英寸墨水屏 (epd3in52)
- **Python版本**: Python 3.x
- **部署时间**: 2025年9月5日

---

## 故障1: 墨水屏驱动不兼容

### 问题描述
部署完成后，系统运行正常，但墨水屏无法正常显示内容。日志显示系统初始化成功，但屏幕没有任何变化。

### 故障现象
```bash
INFO:__main__:Daily Word E-Paper Display v1.0.0 启动
INFO:__main__:墨水屏控制器初始化完成 (epd2in13_V4, 250x122分辨率)
INFO:__main__:所有组件正常加载
# 但墨水屏实际无显示
```

### 排查思路

1. **检查硬件连接**: 确认墨水屏与树莓派的SPI连接正常
2. **验证驱动兼容性**: 对比项目代码与用户现有工作代码
3. **分析驱动差异**: 识别驱动库和配置的不同之处

### 排查过程

#### 步骤1: 检查用户现有工作代码
```bash
# 发现用户crontab中有工作的墨水屏显示任务
crontab -l
# 输出显示每5分钟运行的display_epaper.py脚本
```

#### 步骤2: 对比驱动差异
```bash
# 检查用户工作代码使用的驱动
cat ~/Downloads/e-Paper/RaspberryPi_JetsonNano/python/examples/display_epaper.py
```

**关键发现**:
- 用户工作代码使用 `waveshare_epd.epd3in52` 驱动
- 项目代码使用自定义的低级驱动实现
- 墨水屏型号不匹配: 项目默认 `epd2in13_V4` vs 实际 `epd3in52`

#### 步骤3: 分析依赖缺失
```bash
# 检查必要的库文件
find /usr -name "*epd*" -o -name "*waveshare*"
ls -la ~/Downloads/e-Paper/RaspberryPi_JetsonNano/python/lib/
```

**发现问题**:
- 缺少 `waveshare_epd` 库
- 缺少字体文件 `Font.ttc`
- 缺少辅助模块 `text_wrap.py`, `get_ipaddress.py`

### 解决方案

#### 方案1: 复制用户工作环境的驱动文件
```bash
# 复制waveshare_epd库
cp -r ~/Downloads/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd /opt/daily-word-epaper/src/

# 复制字体文件
mkdir -p /opt/daily-word-epaper/pic
cp ~/Downloads/e-Paper/RaspberryPi_JetsonNano/python/pic/Font.ttc /opt/daily-word-epaper/pic/

# 复制辅助模块
cp ~/Downloads/e-Paper/RaspberryPi_JetsonNano/python/examples/text_wrap.py /opt/daily-word-epaper/src/
cp ~/Downloads/e-Paper/RaspberryPi_JetsonNano/python/examples/get_ipaddress.py /opt/daily-word-epaper/src/
```

#### 方案2: 创建兼容的墨水屏控制器
基于用户工作代码创建新的显示控制器:

```python
#!/usr/bin/env python3
"""
每日单词墨水屏显示控制器 - 基于用户工作代码
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from waveshare_epd import epd3in52
from PIL import Image, ImageDraw, ImageFont
import text_wrap
import logging

class EpaperController:
    def __init__(self):
        self.epd = epd3in52.EPD()
        self.width = self.epd.width
        self.height = self.epd.height
        
    def display_content(self, word, definition, sentence):
        # 基于用户工作代码的显示逻辑
        # ...
```

#### 方案3: 安装缺失的Python依赖
```bash
# 安装gpiozero库
cd /opt/daily-word-epaper && ./venv/bin/pip install gpiozero
```

### 验证解决方案
```bash
# 测试新的墨水屏控制器
cd /opt/daily-word-epaper && ./venv/bin/python src/daily_word_epaper_controller.py

# 预期输出:
# INFO:__main__:墨水屏控制器初始化成功
# INFO:__main__:开始墨水屏测试显示...
# INFO:__main__:测试显示完成
```

---

## 故障2: 服务冲突问题

### 问题描述
部署的新系统与用户现有的crontab墨水屏任务产生冲突，导致显示内容被覆盖。

### 故障现象
- 新系统显示内容后，很快被crontab任务覆盖
- 两个系统同时访问墨水屏硬件资源

### 排查思路
1. **检查系统进程**: 识别所有访问墨水屏的进程
2. **分析crontab配置**: 找出冲突的定时任务
3. **协调资源访问**: 避免多个进程同时操作硬件

### 解决方案

#### 注释冲突的crontab任务
```bash
# 备份原crontab
crontab -l > /tmp/crontab_backup

# 创建新的crontab配置，注释掉冲突任务
cat > /tmp/new_crontab << 'EOF'
# 原有的墨水屏显示任务已注释，避免与新系统冲突
# */5 * * * * cd /home/admin/Downloads/e-Paper/RaspberryPi_JetsonNano/python/examples && /usr/bin/python3 display_epaper.py

# 其他非冲突任务保持不变
# ...
EOF

# 应用新配置
crontab /tmp/new_crontab
```

---

## 故障3: 更新频率配置问题

### 问题描述
需要将系统更新频率从默认配置改为每10分钟更新一次。

### 解决方案

#### 修改配置文件
```python
# 在 daily_word_config.py 中修改 UPDATE_CONFIG
UPDATE_CONFIG = {
    'mode': 'interval',  # 改为间隔模式
    'interval_seconds': 600,  # 10分钟 = 600秒
    'schedule_times': [],  # 间隔模式下此项无效
    'retry_interval': 300,  # 失败重试间隔5分钟
    'max_retries': 3
}
```

#### 重启服务应用配置
```bash
daily-word restart
```

---

## 故障4: 依赖库安装问题

### 问题描述
系统运行时提示缺少 `gpiozero` 模块。

### 故障现象
```
ModuleNotFoundError: No module named 'gpiozero'
```

### 解决方案
```bash
# 在虚拟环境中安装缺失依赖
cd /opt/daily-word-epaper && ./venv/bin/pip install gpiozero
```

---

## 部署最佳实践

### 1. 环境检查清单

部署前必须检查的项目:

- [ ] 确认墨水屏型号和驱动兼容性
- [ ] 检查现有系统是否有冲突的墨水屏服务
- [ ] 验证必要的库文件和字体文件存在
- [ ] 确认Python依赖完整安装

### 2. 驱动兼容性验证

```bash
# 检查墨水屏型号
dmesg | grep -i spi
lsmod | grep spi

# 测试现有驱动
python3 -c "from waveshare_epd import epd3in52; print('驱动可用')"
```

### 3. 资源冲突检查

```bash
# 检查占用墨水屏的进程
ps aux | grep -E "(epd|display|epaper)"

# 检查crontab任务
crontab -l | grep -E "(epd|display|epaper)"

# 检查systemd服务
systemctl list-units | grep -E "(epd|display|epaper)"
```

### 4. 部署验证步骤

```bash
# 1. 测试墨水屏硬件
python3 src/daily_word_epaper_controller.py

# 2. 验证服务启动
daily-word start
daily-word status

# 3. 检查日志
daily-word logs

# 4. 测试更新功能
daily-word update
```

---

## 常见问题FAQ

### Q1: 墨水屏显示空白或花屏
**A**: 检查驱动兼容性，确认使用正确的墨水屏型号驱动。

### Q2: 系统提示权限错误
**A**: 确认运行用户有GPIO访问权限，必要时使用sudo运行。

### Q3: 字体显示异常
**A**: 检查字体文件路径，确保Font.ttc文件存在且可读。

### Q4: 服务无法启动
**A**: 检查Python虚拟环境和依赖安装，查看详细错误日志。

---

## 联系信息

如遇到本文档未涵盖的问题，请:

1. 查看系统日志: `daily-word logs`
2. 检查服务状态: `daily-word status`
3. 运行系统测试: `daily-word test`

---

**文档版本**: v1.0  
**最后更新**: 2025年9月5日  
**适用版本**: Daily Word E-Paper Display v1.0.0