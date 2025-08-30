# 系统要求

## 📋 概述

本章节详细说明运行每日单词墨水屏显示系统所需的硬件和软件要求。请在开始安装前仔细检查所有要求。

## 🖥️ 硬件要求

### 树莓派要求

| 组件 | 最低要求 | 推荐配置 | 说明 |
|------|----------|----------|------|
| **主板** | Raspberry Pi 4B | Raspberry Pi 5 | 支持GPIO和SPI接口 |
| **内存** | 2GB RAM | 4GB+ RAM | 更多内存提供更好性能 |
| **存储** | 16GB MicroSD | 32GB+ Class 10 | 高速卡提供更好体验 |
| **电源** | 5V/3A | 5V/3A 官方电源 | 稳定电源确保系统稳定 |

### 墨水屏要求

#### 支持的墨水屏型号

| 品牌 | 型号 | 尺寸 | 分辨率 | 接口 | 状态 |
|------|------|------|--------|------|------|
| Waveshare | 2.7inch e-Paper HAT | 2.7" | 264×176 | SPI | ✅ 完全支持 |
| Waveshare | 4.2inch e-Paper HAT | 4.2" | 400×300 | SPI | ✅ 完全支持 |
| Waveshare | 2.13inch e-Paper HAT | 2.13" | 250×122 | SPI | ⚠️ 实验性支持 |
| Good Display | GDEW027W3 | 2.7" | 264×176 | SPI | ⚠️ 需要适配 |

#### 连接要求

- **SPI接口：** 必须支持SPI通信
- **GPIO引脚：** 需要至少4个GPIO引脚（RST, DC, CS, BUSY）
- **电源：** 3.3V供电（由树莓派提供）

### 网络要求

| 类型 | 要求 | 说明 |
|------|------|------|
| **网络连接** | WiFi或以太网 | 用于获取每日单词和句子 |
| **带宽** | 最低1Mbps | API请求数据量很小 |
| **稳定性** | 建议稳定连接 | 支持离线模式，但需要定期联网更新 |

## 💻 软件要求

### 操作系统

| 系统 | 版本 | 架构 | 状态 |
|------|------|------|------|
| **Raspberry Pi OS** | Bullseye (11) 或更新 | ARM64/ARM32 | ✅ 推荐 |
| **Ubuntu** | 20.04+ | ARM64 | ✅ 支持 |
| **Debian** | 11+ | ARM64/ARM32 | ⚠️ 未测试 |

### Python环境

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| **Python** | 3.8+ | 系统默认Python版本 |
| **pip** | 最新版本 | Python包管理器 |
| **venv** | 内置模块 | 虚拟环境支持 |

### 系统服务

| 服务 | 状态 | 说明 |
|------|------|------|
| **SPI** | 必须启用 | 墨水屏通信接口 |
| **GPIO** | 必须可用 | 控制墨水屏引脚 |
| **systemd** | 必须运行 | 服务管理 |
| **cron** | 推荐启用 | 定时任务支持 |

## 🔍 系统检查

### 自动检查脚本

运行以下命令检查系统是否满足要求：

```bash
# 下载检查脚本
curl -sSL https://raw.githubusercontent.com/your-repo/main/docs/assets/scripts/check-requirements.sh -o check-requirements.sh

# 运行检查
chmod +x check-requirements.sh
./check-requirements.sh
```

### 手动检查步骤

#### 1. 检查树莓派型号

```bash
# 查看硬件信息
cat /proc/cpuinfo | grep "Model"

# 预期输出示例：
# Model           : Raspberry Pi 4 Model B Rev 1.4
```

#### 2. 检查内存

```bash
# 查看内存信息
free -h

# 预期输出示例：
#               total        used        free      shared  buff/cache   available
# Mem:           3.8Gi       200Mi       3.2Gi        50Mi       400Mi       3.4Gi
```

#### 3. 检查存储空间

```bash
# 查看磁盘空间
df -h /

# 预期输出示例：
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/root        30G  2.5G   26G  10% /
```

#### 4. 检查Python版本

```bash
# 检查Python版本
python3 --version

# 预期输出：Python 3.9.x 或更高版本
```

#### 5. 检查SPI接口

```bash
# 检查SPI设备
ls /dev/spi*

# 预期输出：
# /dev/spidev0.0  /dev/spidev0.1
```

#### 6. 检查GPIO访问

```bash
# 检查GPIO组权限
groups $USER | grep -o gpio

# 预期输出：gpio
```

## ⚙️ 系统优化建议

### 性能优化

```bash
# 1. 增加GPU内存分配
echo "gpu_mem=64" | sudo tee -a /boot/config.txt

# 2. 启用硬件随机数生成器
echo "dtparam=random=on" | sudo tee -a /boot/config.txt

# 3. 优化SD卡性能
echo "dtparam=sd_overclock=100" | sudo tee -a /boot/config.txt
```

### 电源管理

```bash
# 禁用不必要的服务以节省电力
sudo systemctl disable bluetooth
sudo systemctl disable wifi-powersave@wlan0
```

### 安全设置

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 启用防火墙
sudo ufw enable

# 配置SSH安全
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
```

## 🚨 常见问题

### Q: 我的树莓派是3B+，可以运行吗？

**A:** 理论上可以，但不推荐。树莓派3B+的性能可能不足以流畅运行系统，特别是在处理图像和网络请求时。

### Q: 可以使用其他品牌的墨水屏吗？

**A:** 可以，但需要适配驱动程序。系统设计时考虑了扩展性，可以通过修改配置文件支持其他墨水屏。

### Q: 系统对网络的依赖程度如何？

**A:** 系统支持离线模式，本地缓存了备用内容。但为了获取最新的每日单词和句子，建议保持网络连接。

### Q: 可以在虚拟机中测试吗？

**A:** 可以测试软件逻辑，但无法测试墨水屏显示功能，因为虚拟机无法访问GPIO接口。

## ✅ 检查清单

安装前请确认以下项目：

- [ ] 树莓派4/5正常运行
- [ ] 内存≥2GB，推荐4GB+
- [ ] 存储空间≥16GB，推荐32GB+
- [ ] 网络连接正常
- [ ] Python 3.8+已安装
- [ ] SPI接口已启用
- [ ] 用户在gpio组中
- [ ] 墨水屏硬件准备就绪

## 📊 性能基准

### 预期性能指标

| 指标 | 树莓派4 (4GB) | 树莓派5 (8GB) |
|------|---------------|---------------|
| **启动时间** | 15-20秒 | 10-15秒 |
| **更新时间** | 30-45秒 | 20-30秒 |
| **内存使用** | 150-200MB | 100-150MB |
| **CPU使用** | 5-10% (空闲时) | 3-8% (空闲时) |

---

**下一步：** [硬件连接设置](02-hardware-setup.md)