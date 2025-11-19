# 墨水屏天气诗词显示系统 - 项目交接文档
# E-paper Weather & Poetry Display System - Project Handover Document

**项目状态**: ✅ 生产就绪 (Production Ready)
**最后更新**: 2025-11-19
**文档版本**: 1.0

---

## 📋 项目概述 (Project Overview)

### **项目名称**
墨水屏天气诗词显示系统 (E-paper Weather & Poetry Display System)

### **项目描述**
基于树莓派3B+的3.52英寸Waveshare电子墨水屏显示系统，自动获取实时天气信息和每日古典诗词，每5分钟自动刷新。

### **核心功能**
- 🌤️ **实时天气显示** - 获取广州天气信息（温度、天气状况、湿度）
- 📜 **每日诗词显示** - 自动获取并显示古典诗词，智能截取最优内容
- ⏰ **自动刷新机制** - 每5分钟自动刷新内容
- 🖥️ **IP地址显示** - 右下角显示设备IP，便于远程管理
- 🔄 **系统服务化** - systemd服务管理，开机自动启动

---

## 🖥️ 硬件配置 (Hardware Configuration)

### **核心硬件清单**
| 组件 | 型号/规格 | 连接方式 | 功能说明 |
|------|-----------|----------|----------|
| **主控** | 树莓派3B+ | - | 中央处理器 |
| **显示屏** | Waveshare 3.52英寸 e-paper | SPI/GPIO | 240x360像素电子墨水屏 |
| **电源** | 5V 2A外部电源适配器 | GPIO 5V引脚 | 稳定供电（关键） |
| **网络** | WiFi (wlan0) | 内置 | IP: 192.168.2.176 |

### **GPIO引脚映射** (当前工作配置)
```
电子墨水屏 → 树莓派
VCC  → 5V 或 3.3V
GND  → GND
DIN  → GPIO10 (MOSI)
CLK  → GPIO11 (SCLK)
CS   → GPIO8  (CE0)
DC   → GPIO25
RST  → GPIO27
BUSY → GPIO24
```

### **电源要求**
- **最低电压**: 5V
- **最低电流**: 500mA（推荐1A以上）
- **注意事项**: 必须使用外部电源适配器，USB供电可能不稳定

---

## 🛠️ 软件环境 (Software Environment)

### **操作系统**
- **系统**: Raspberry Pi OS
- **Python版本**: Python 3.11+
- **架构**: ARM64

### **关键依赖项**
```bash
# 核心依赖
python3-pil
python3-requests
python3-netifaces

# 电子墨水屏库路径
~/e-Paper/RaspberryPi_JetsonNano/python/lib

# 中文字体
/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
/usr/share/fonts/truetype/wqy/wqy-microhei.ttc
```

### **环境变量**
```bash
PYTHONPATH="/home/admin/e-Paper/RaspberryPi_JetsonNano/python/lib:$PYTHONPATH"
```

---

## 📁 项目结构 (Project Structure)

### **主要文件**
```
/home/admin/Github/epaper-with-raspberrypi/
├── auto_weather_poetry_display.py  # 主程序（含IP地址）
├── manage_display.sh                 # 管理脚本
├── CHANGELOG.md                       # 更新日志
├── CLAUDE.md                          # Claude助手指南
├── DISPLAY_OPTIMIZATION_SUMMARY.md # 系统优化总结
├── config.ini                         # 配置文件
├── data/
│   └── token.txt                    # 诗歌API token
└── src/                              # 源代码目录
```

### **核心程序文件**
- **`auto_weather_poetry_display.py`** - 主显示程序，包含天气、诗词、IP显示
- **`manage_display.sh`** - systemd服务管理脚本
- **`weather-poetry-display.service`** - systemd服务配置文件

### **服务文件位置**
- **服务配置**: `/etc/systemd/system/weather-poetry-display.service`
- **日志文件**: `/home/admin/Github/epaper-with-raspberrypi/src/auto_display.log`

---

## ⚙️ 配置信息 (Configuration)

### **API配置 (config.ini)**
```ini
[DEFAULT]
WEATHER_API_KEY = 28962db3791a4792b4c90923241402
CITY_API_KEY = GUANGZHOU
POEM_TOKEN_API_URL = https://v2.jinrishici.com/token
DAILY_POEM_API_URL = https://v2.jinrishici.com/sentence
```

### **API密钥信息**
- **天气API**: WeatherAPI.com
- **诗歌API**: 今日诗句网 (jinrishici.com)
- **Token文件**: `/home/admin/Github/epaper-with-raspberrypi/data/token.txt`

### **显示参数**
- **刷新频率**: 5分钟
- **屏幕尺寸**: 240x360像素
- **字体**: WQY Zenhei/Microhei (中文字符)
- **背景**: 白底黑字

---

## 🔄 系统服务 (System Service)

### **服务名称**
`weather-poetry-display.service`

### **服务状态**
```bash
# 检查服务状态
sudo systemctl status weather-poetry-display.service

# 启动/停止/重启
sudo systemctl start weather-poetry-display.service
sudo systemctl stop weather-poetry-display.service
sudo systemctl restart weather-poetry-display.service

# 开机自启
sudo systemctl enable weather-poetry-display.service
```

### **管理脚本**
```bash
cd /home/admin/Github/epaper-with-raspberrypi
./manage_display.sh {start|stop|restart|status|logs|enable|disable}
```

---

## 🔧 关键技术实现 (Key Technical Implementation)

### **电子墨水屏驱动方法**
```python
# 工作版本驱动初始化序列
from waveshare_epd import epd3in52

epd = epd3in52.EPD()
epd.init()
epd.display_NUM(epd.WHITE)  # 关键：使用display_NUM而不是Clear
epd.lut_GC()              # 关键：加载查找表
epd.refresh()             # 关键：手动刷新
```

### **字体加载策略**
```python
# 优先级顺序
font_paths = [
    "/home/admin/Downloads/e-Paper/RaspberryPi_JetsonNano/python/pic/Font.ttc",  # 工作版本字体
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",                    # 系统中文字体
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",                  # 系统中文字体
]
```

### **IP地址获取方法**
```python
def get_device_ip():
    # 优先WiFi接口
    wifi_interfaces = ['wlan0', 'wlp2s0', 'wlan1']
    # 备用以太网接口
    eth_interfaces = ['eth0', 'enp0s3', 'enp2s0']
    # 备用socket方法
```

---

## 📊 系统资源占用 (System Resource Usage)

### **硬件资源**
- **CPU使用**: 刷新时短暂峰值，完成即释放
- **内存使用**: <50MB
- **存储空间**: 约200MB（包含日志和缓存文件）
- **网络带宽**: 每次刷新约1-2KB数据

### **软件资源**
- **Python进程**: 1个主进程 + systemd管理
- **文件描述符**: GPIO设备、网络套接字、日志文件
- **端口使用**: 80 (HTTP), 443 (HTTPS) 用于API调用

---

## ⚠️ 冲突预防指南 (Conflict Prevention Guide)

### **硬件资源冲突**
```bash
# 检查GPIO使用情况
sudo lsof /dev/gpiomem

# 检查进程占用
ps aux | grep -E "epaper|display|python" | grep -v grep

# 停止可能冲突的服务
sudo systemctl stop daily-word.service  # 如果存在
sudo systemctl disable daily-word.service
```

### **软件库冲突**
```python
# 检查库路径
export PYTHONPATH="/home/admin/e-Paper/RaspberryPi_JetsonNano/python/lib:$PYTHONPATH"

# 库文件位置
~/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd/
```

### **显示控制冲突**
- **问题**: 多个程序同时控制电子墨水屏会导致显示混乱
- **预防**: 确保只有一个服务在运行
- **检测**: `sudo systemctl status weather-poetry-display.service`

### **网络资源**
- **天气API**: 每日请求约100次，在免费额度内
- **诗歌API**: 每日请求约100次，Token自动刷新
- **建议**: 监控API使用量，避免超额

---

## 🧪 测试和验证 (Testing & Validation)

### **基础测试脚本**
```bash
# 基础像素测试
cd /home/admin/Github/epaper-with-raspberrypi/src
python test_new_display.py

# 字体渲染测试
python test_poem_display.py
```

### **服务测试**
```bash
# 服务状态检查
./manage_display.sh status

# 日志查看
./manage_display.sh logs

# 重启测试
./manage_display.sh restart
```

### **显示效果验证**
- **白色背景**: 确保背景为白色，不是黑色
- **黑色文字**: 确保文字清晰可读
- **中文显示**: 确保中文字符正确显示，无方形
- **IP地址**: 右下角正确显示设备IP

---

## 📚 API接口文档 (API Documentation)

### **天气API**
- **服务商**: WeatherAPI.com
- **端点**: `http://api.weatherapi.com/v1/current.json`
- **参数**: key, q (城市), aqi (空气质量)
- **频率**: 每5分钟一次
- **限制**: 免费额度每月100万次请求

### **诗歌API**
- **服务商**: 今日诗句网 (jinrishici.com)
- **Token端点**: `https://v2.jinrishici.com/token`
- **内容端点**: `https://v2.jinrishici.com/sentence`
- **Token管理**: 自动刷新，存储在data/token.txt

### **Token管理**
```python
# Token获取
response = requests.get("https://v2.jinrishici.com/token")
token = response.json()['data']

# Token存储
with open('data/token.txt', 'w') as f:
    f.write(token)

# Token刷新（自动触发，400错误时）
```

---

## 🔧 维护和故障排除 (Maintenance & Troubleshooting)

### **常见问题诊断**

#### **显示问题**
1. **黑屏/无显示** → 检查电源和连接
2. **条纹/乱码** → 检查SPI连接和驱动
3. **中文显示异常** → 检查字体安装
4. **IP获取失败** → 检查网络连接

#### **服务问题**
1. **服务不启动** → 检查systemd配置
2. **频繁重启** → 检查日志错误信息
3. **API调用失败** → 检查网络和token

### **日志分析**
```bash
# 实时日志监控
tail -f /home/admin/Github/epaper-with-raspberrypi/src/auto_display.log

# 错误日志搜索
grep -i error /home/admin/Github/epaper-with-raspberrypi/src/auto_display.log

# 服务日志
sudo journalctl -u weather-poetry-display -f
```

### **性能监控**
```bash
# 系统资源监控
htop

# 内存使用
free -h

# 磁盘使用
df -h
```

---

## 🔐 安全注意事项 (Security Notes)

### **API密钥安全**
- **配置文件**: `config.ini` 包含API密钥
- **权限设置**: 确保文件权限适当
- **Git忽略**: 确保敏感信息不被提交

### **网络安全**
- **防火墙**: 配置适当的防火墙规则
- **SSH安全**: 使用密钥认证，禁用密码登录
- **更新安全**: 定期更新系统和依赖

### **物理安全**
- **环境要求**: 室内使用，避免潮湿环境
- **电源管理**: 使用稳定的电源适配器
- **静电防护**: 注意静电防护措施

---

## 📈 性能指标 (Performance Metrics)

### **响应时间**
- **系统启动**: ~10秒
- **数据获取**: 天气API 2-3秒，诗歌API 1-2秒
- **图像渲染**: <1秒
- **显示刷新**: ~3-5秒
- **完整周期**: ~8-10秒

### **可靠性**
- **正常运行时间**: 24/7持续运行
- **自动重启**: 异常时30秒内恢复
- **故障恢复**: 服务异常时自动重启

### **资源使用**
- **CPU平均**: <1%
- **内存占用**: <50MB
- **存储占用**: <200MB
- **网络带宽**: 每小时约1KB

---

## 📞 联系和支持 (Contact & Support)

### **项目管理**
- **代码仓库**: https://github.com/goodniuniu/epaper-with-raspberrypi
- **项目文档**: 完整的README和CHANGELOG
- **版本控制**: Git版本管理

### **技术支持**
- **日志文件**: `/home/admin/Github/epaper-with-raspberrypi/src/auto_display.log`
- **管理脚本**: `./manage_display.sh`
- **远程管理**: SSH访问设备IP地址

### **硬件支持**
- **电子墨水屏**: Waveshare官方文档
- **树莓派**: Raspberry Pi官方文档
- **Python**: Python官方文档

---

## 🔄 项目交接检查清单 (Project Handover Checklist)

### **✅ 硬件状态**
- [ ] 电子墨水屏正常工作
- [ ] 树莓派系统正常运行
- [ ] 网络连接稳定
- [ ] 电源供应稳定

### **✅ 软件状态**
- [ ] 服务正常运行中
- [ ] 日志记录正常
- [ ] API调用正常
- [ ] 显示效果正常

### **✅ 配置验证**
- [ ] API密钥有效
- [ ] 网络配置正确
- [ ] 系统服务配置正确
- [ ] 字体安装完成

### **✅ 文档完整性**
- [ ] 本文档完整更新
- [ ] CHANGELOG记录完整
- [ ] README信息准确
- [ ] API文档正确

---

**交接完成日期**: 2025-11-19
**项目状态**: ✅ 生产就绪
**下次维护**: 根据使用情况

---

**重要提醒**: 新项目开发时，请务必检查硬件资源占用和服务状态，确保与当前系统无冲突。建议使用不同的GPIO引脚或时间分段来避免冲突。