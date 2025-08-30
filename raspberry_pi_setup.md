# 树莓派4部署指南 - 每日单词墨水屏显示系统

本指南将帮助您在树莓派4上部署每日单词显示系统。

## 系统要求

- 树莓派4 (推荐4GB内存版本)
- Raspberry Pi OS (Bullseye或更新版本)
- 墨水屏模块 (如Waveshare 2.7寸或类似)
- 网络连接 (WiFi或以太网)

## 1. 系统准备

### 更新系统
```bash
sudo apt update && sudo apt upgrade -y
```

### 安装Python依赖
```bash
# 安装Python3和pip
sudo apt install python3 python3-pip python3-venv -y

# 安装系统级依赖
sudo apt install git curl wget -y

# 安装图像处理库
sudo apt install python3-pil python3-numpy -y

# 安装字体
sudo apt install fonts-dejavu fonts-dejavu-core fonts-dejavu-extra -y
```

### 启用SPI接口 (墨水屏需要)
```bash
sudo raspi-config
# 选择 Interfacing Options -> SPI -> Enable
# 或者直接编辑配置文件
echo 'dtparam=spi=on' | sudo tee -a /boot/config.txt
```

## 2. 项目部署

### 克隆项目
```bash
cd /home/pi
git clone <your-repo-url> epaper-daily-word
cd epaper-daily-word
```

### 创建Python虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

### 安装Python依赖
```bash
pip install --upgrade pip
pip install requests pathlib pillow numpy

# 如果使用Waveshare墨水屏
pip install waveshare-epd

# 或者安装通用墨水屏库
pip install luma.epd
```

## 3. 硬件连接

### 墨水屏连接 (以Waveshare 2.7寸为例)
```
墨水屏    ->  树莓派4
VCC      ->  3.3V (Pin 1)
GND      ->  GND (Pin 6)
DIN      ->  GPIO10 (Pin 19, MOSI)
CLK      ->  GPIO11 (Pin 23, SCLK)
CS       ->  GPIO8 (Pin 24, CE0)
DC       ->  GPIO25 (Pin 22)
RST      ->  GPIO17 (Pin 11)
BUSY     ->  GPIO24 (Pin 18)
```

## 4. 配置文件调整

创建树莓派专用配置：

```bash
cp src/word_config.py src/word_config_rpi.py
```

然后编辑配置文件以适配树莓派：

## 5. 快速安装

使用自动安装脚本：

```bash
# 下载并运行安装脚本
curl -sSL https://raw.githubusercontent.com/your-repo/install_rpi.sh | bash

# 或者手动下载后运行
wget https://raw.githubusercontent.com/your-repo/install_rpi.sh
chmod +x install_rpi.sh
./install_rpi.sh
```

## 6. 手动安装步骤

如果自动安装失败，可以按以下步骤手动安装：

### 6.1 复制项目文件

```bash
# 复制所有源文件到树莓派
scp -r src/ pi@your-pi-ip:~/daily-word-epaper/
scp -r data/ pi@your-pi-ip:~/daily-word-epaper/
scp README_daily_word.md pi@your-pi-ip:~/daily-word-epaper/
```

### 6.2 安装墨水屏库

**Waveshare墨水屏:**
```bash
cd ~
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python
sudo python3 setup.py install
```

**Luma.EPD库:**
```bash
pip install luma.epd
```

## 7. 配置和测试

### 7.1 配置墨水屏类型

编辑 `src/word_config_rpi.py`：

```python
DISPLAY_CONFIG = {
    # 根据你的墨水屏型号选择
    'epd_type': 'waveshare_2in7',  # 或 'waveshare_4in2', 'luma_epd'
    'width': 264,   # 根据实际屏幕调整
    'height': 176,  # 根据实际屏幕调整
    # ... 其他配置
}
```

### 7.2 运行测试

```bash
cd ~/daily-word-epaper
source venv/bin/activate
python src/daily_word_rpi.py --test
```

### 7.3 手动更新显示

```bash
python src/daily_word_rpi.py --mode once
```

## 8. 自动化运行

### 8.1 使用Cron定时任务

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每日8点、12点、18点更新）
0 8,12,18 * * * cd /home/pi/daily-word-epaper && ./venv/bin/python src/daily_word_rpi.py --mode scheduled
```

### 8.2 使用systemd服务

创建服务文件 `/etc/systemd/system/daily-word.service`：

```ini
[Unit]
Description=Daily Word E-Paper Display
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/daily-word-epaper
Environment=PATH=/home/pi/daily-word-epaper/venv/bin
ExecStart=/home/pi/daily-word-epaper/venv/bin/python /home/pi/daily-word-epaper/src/daily_word_rpi.py --mode scheduled
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable daily-word
sudo systemctl start daily-word
```

## 9. 管理和维护

### 9.1 使用管理脚本

```bash
# 使用提供的管理脚本
./manage.sh test      # 测试运行
./manage.sh update    # 手动更新
./manage.sh logs      # 查看日志
./manage.sh clear     # 清空显示
./manage.sh status    # 查看服务状态
```

### 9.2 查看日志

```bash
# 查看应用日志
tail -f data/daily_word.log

# 查看系统服务日志
sudo journalctl -u daily-word -f
```

### 9.3 监控系统状态

```bash
# 检查CPU温度
vcgencmd measure_temp

# 检查内存使用
free -h

# 检查磁盘空间
df -h
```

## 10. 故障排除

### 10.1 常见问题

**SPI未启用:**
```bash
# 检查SPI是否启用
ls /dev/spi*
# 如果没有输出，需要启用SPI
sudo raspi-config
```

**权限问题:**
```bash
# 添加用户到spi组
sudo usermod -a -G spi pi
# 重新登录生效
```

**墨水屏不显示:**
```bash
# 检查硬件连接
# 检查库是否正确安装
python3 -c "import epd2in7; print('OK')"
```

**网络连接问题:**
```bash
# 测试网络连接
ping -c 3 api.quotable.io
curl -I https://api.quotable.io/random
```

### 10.2 调试模式

```bash
# 启用调试日志
export DEBUG=1
python src/daily_word_rpi.py --test

# 查看详细错误信息
python src/daily_word_rpi.py --test 2>&1 | tee debug.log
```

## 11. 性能优化

### 11.1 降低功耗

- 启用低功耗模式
- 设置合理的更新间隔
- 墨水屏不使用时进入睡眠模式

### 11.2 提高稳定性

- 设置看门狗定时器
- 添加异常恢复机制
- 定期清理日志文件

## 12. 扩展功能

### 12.1 添加传感器

```python
# 在word_config_rpi.py中添加传感器配置
SENSOR_CONFIG = {
    'temperature_sensor': True,
    'humidity_sensor': True,
    'light_sensor': False
}
```

### 12.2 Web界面

可以添加简单的Web界面来远程管理：

```bash
pip install flask
# 创建简单的Web管理界面
```

### 12.3 多语言支持

修改配置文件支持中英文切换：

```python
LANGUAGE_CONFIG = {
    'default_language': 'en',  # 'en' 或 'zh'
    'fallback_language': 'en'
}
```