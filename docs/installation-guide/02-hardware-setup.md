# 硬件连接设置

## 📋 概述

本章节将指导您正确连接墨水屏与树莓派，确保硬件连接稳定可靠。请严格按照步骤操作，避免因连接错误导致的硬件损坏。

## ⚠️ 安全注意事项

**在开始连接前，请务必：**

- 🔌 **断开树莓派电源**
- 🧤 **佩戴防静电手环**（推荐）
- 🔍 **仔细核对引脚编号**
- 📖 **参考墨水屏官方文档**

## 🔌 GPIO引脚说明

### 树莓派GPIO布局

```
树莓派4/5 GPIO引脚布局 (40-pin)

     3V3  (1) (2)  5V
   GPIO2  (3) (4)  5V
   GPIO3  (5) (6)  GND
   GPIO4  (7) (8)  GPIO14
     GND  (9) (10) GPIO15
  GPIO17 (11) (12) GPIO18
  GPIO27 (13) (14) GND
  GPIO22 (15) (16) GPIO23
     3V3 (17) (18) GPIO24
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25
  GPIO11 (23) (24) GPIO8
     GND (25) (26) GPIO7
   GPIO0 (27) (28) GPIO1
   GPIO5 (29) (30) GND
   GPIO6 (31) (32) GPIO12
  GPIO13 (33) (34) GND
  GPIO19 (35) (36) GPIO16
  GPIO26 (37) (38) GPIO20
     GND (39) (40) GPIO21
```

## 📱 墨水屏连接方案

### Waveshare 2.7寸 e-Paper HAT

#### 标准连接方式

| 墨水屏引脚 | 功能 | 树莓派引脚 | BCM编号 | 物理引脚 |
|------------|------|------------|---------|----------|
| VCC | 电源(3.3V) | 3V3 | - | Pin 1 |
| GND | 接地 | GND | - | Pin 6 |
| DIN | 数据输入 | MOSI | GPIO10 | Pin 19 |
| CLK | 时钟 | SCLK | GPIO11 | Pin 23 |
| CS | 片选 | CE0 | GPIO8 | Pin 24 |
| DC | 数据/命令 | GPIO25 | GPIO25 | Pin 22 |
| RST | 复位 | GPIO17 | GPIO17 | Pin 11 |
| BUSY | 忙状态 | GPIO24 | GPIO24 | Pin 18 |

#### 连接示意图

```
墨水屏                    树莓派4/5
┌─────────┐              ┌─────────┐
│   VCC   │──────────────│ 3V3(1)  │
│   GND   │──────────────│ GND(6)  │
│   DIN   │──────────────│GPIO10(19)│
│   CLK   │──────────────│GPIO11(23)│
│   CS    │──────────────│GPIO8(24) │
│   DC    │──────────────│GPIO25(22)│
│   RST   │──────────────│GPIO17(11)│
│   BUSY  │──────────────│GPIO24(18)│
└─────────┘              └─────────┘
```

### Waveshare 4.2寸 e-Paper HAT

#### 连接方式（与2.7寸相同）

| 墨水屏引脚 | 功能 | 树莓派引脚 | BCM编号 | 物理引脚 |
|------------|------|------------|---------|----------|
| VCC | 电源(3.3V) | 3V3 | - | Pin 1 |
| GND | 接地 | GND | - | Pin 6 |
| DIN | 数据输入 | MOSI | GPIO10 | Pin 19 |
| CLK | 时钟 | SCLK | GPIO11 | Pin 23 |
| CS | 片选 | CE0 | GPIO8 | Pin 24 |
| DC | 数据/命令 | GPIO25 | GPIO25 | Pin 22 |
| RST | 复位 | GPIO17 | GPIO17 | Pin 11 |
| BUSY | 忙状态 | GPIO24 | GPIO24 | Pin 18 |

## 🔧 连接步骤

### 步骤1：准备工作

1. **关闭树莓派电源**
   ```bash
   sudo shutdown -h now
   ```

2. **准备连接线**
   - 8根杜邦线（母对母）
   - 或使用墨水屏配套的连接线

3. **准备工具**
   - 小螺丝刀（如需要）
   - 防静电手环（推荐）

### 步骤2：连接电源线

⚠️ **重要：先连接GND，再连接VCC**

1. **连接GND（接地）**
   ```
   墨水屏 GND → 树莓派 Pin 6 (GND)
   ```

2. **连接VCC（电源）**
   ```
   墨水屏 VCC → 树莓派 Pin 1 (3V3)
   ```

### 步骤3：连接SPI信号线

1. **连接SPI数据线**
   ```
   墨水屏 DIN → 树莓派 Pin 19 (GPIO10/MOSI)
   墨水屏 CLK → 树莓派 Pin 23 (GPIO11/SCLK)
   墨水屏 CS  → 树莓派 Pin 24 (GPIO8/CE0)
   ```

### 步骤4：连接控制信号线

1. **连接控制线**
   ```
   墨水屏 DC   → 树莓派 Pin 22 (GPIO25)
   墨水屏 RST  → 树莓派 Pin 11 (GPIO17)
   墨水屏 BUSY → 树莓派 Pin 18 (GPIO24)
   ```

### 步骤5：连接验证

1. **视觉检查**
   - 确认所有连接牢固
   - 检查是否有短路
   - 确认引脚对应正确

2. **连接测试**
   ```bash
   # 启动树莓派后运行
   gpio readall
   ```

## 🔍 连接验证

### 硬件检测脚本

创建检测脚本验证连接：

```bash
# 创建检测脚本
cat > ~/check_epaper_connection.py << 'EOF'
#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# 定义引脚
RST_PIN = 17
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 24

def check_gpio_pins():
    """检查GPIO引脚连接"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    pins = {
        'RST': RST_PIN,
        'DC': DC_PIN,
        'CS': CS_PIN,
        'BUSY': BUSY_PIN
    }
    
    print("检查GPIO引脚连接...")
    
    for name, pin in pins.items():
        try:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(pin, GPIO.LOW)
            print(f"✅ {name} (GPIO{pin}): 正常")
        except Exception as e:
            print(f"❌ {name} (GPIO{pin}): 错误 - {e}")
    
    GPIO.cleanup()

def check_spi_interface():
    """检查SPI接口"""
    import os
    
    print("\n检查SPI接口...")
    
    if os.path.exists('/dev/spidev0.0'):
        print("✅ SPI接口: 已启用")
        return True
    else:
        print("❌ SPI接口: 未启用")
        print("   请运行: sudo raspi-config")
        print("   选择: Interfacing Options -> SPI -> Enable")
        return False

if __name__ == "__main__":
    print("=== 墨水屏连接检测 ===\n")
    
    check_gpio_pins()
    spi_ok = check_spi_interface()
    
    print("\n=== 检测完成 ===")
    
    if spi_ok:
        print("✅ 硬件连接检查通过")
    else:
        print("❌ 需要启用SPI接口")
EOF

# 运行检测
python3 ~/check_epaper_connection.py
```

### SPI接口测试

```bash
# 测试SPI通信
ls -l /dev/spi*

# 预期输出：
# crw-rw---- 1 root spi 153, 0 Aug 30 10:00 /dev/spidev0.0
# crw-rw---- 1 root spi 153, 1 Aug 30 10:00 /dev/spidev0.1
```

## 🛠️ 自定义连接方案

### 修改GPIO引脚配置

如果需要使用不同的GPIO引脚，请修改配置文件：

```python
# 在 src/word_config_rpi.py 中修改
DISPLAY_CONFIG = {
    'gpio_pins': {
        'rst': 17,    # 复位引脚
        'dc': 25,     # 数据/命令引脚
        'cs': 8,      # 片选引脚
        'busy': 24    # 忙状态引脚
    }
}
```

### 支持的引脚替代方案

| 功能 | 默认引脚 | 可选引脚 | 说明 |
|------|----------|----------|------|
| RST | GPIO17 | GPIO18, GPIO27 | 复位信号 |
| DC | GPIO25 | GPIO22, GPIO23 | 数据/命令选择 |
| CS | GPIO8 | GPIO7 | SPI片选 |
| BUSY | GPIO24 | GPIO23, GPIO18 | 忙状态检测 |

## 🔧 故障排除

### 常见连接问题

#### 问题1：墨水屏无响应

**可能原因：**
- 电源连接错误
- SPI接口未启用
- 引脚连接松动

**解决方案：**
```bash
# 1. 检查SPI接口
sudo raspi-config
# 选择 Interfacing Options -> SPI -> Enable

# 2. 检查连接
python3 ~/check_epaper_connection.py

# 3. 重启系统
sudo reboot
```

#### 问题2：显示内容异常

**可能原因：**
- DC引脚连接错误
- 时序问题
- 电源不稳定

**解决方案：**
```bash
# 检查电源电压
vcgencmd measure_volts

# 检查GPIO状态
gpio readall
```

#### 问题3：系统无法识别墨水屏

**可能原因：**
- CS引脚连接错误
- SPI设备权限问题

**解决方案：**
```bash
# 添加用户到spi组
sudo usermod -a -G spi $USER

# 重新登录使权限生效
logout
```

### 连接质量检查

```bash
# 创建连接质量测试脚本
cat > ~/connection_quality_test.py << 'EOF'
#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import random

def test_pin_stability(pin, test_duration=10):
    """测试引脚稳定性"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    
    print(f"测试GPIO{pin}稳定性 ({test_duration}秒)...")
    
    start_time = time.time()
    toggle_count = 0
    
    while time.time() - start_time < test_duration:
        state = random.choice([GPIO.HIGH, GPIO.LOW])
        GPIO.output(pin, state)
        time.sleep(0.01)
        toggle_count += 1
    
    GPIO.cleanup()
    print(f"✅ GPIO{pin}: 完成{toggle_count}次切换")

if __name__ == "__main__":
    pins = [17, 25, 8, 24]  # RST, DC, CS, BUSY
    
    for pin in pins:
        test_pin_stability(pin, 5)
        time.sleep(1)
EOF

python3 ~/connection_quality_test.py
```

## 📋 连接检查清单

完成连接后，请确认以下项目：

- [ ] 电源连接正确（VCC→3V3, GND→GND）
- [ ] SPI信号线连接正确（DIN, CLK, CS）
- [ ] 控制信号线连接正确（DC, RST, BUSY）
- [ ] 所有连接牢固无松动
- [ ] 无短路现象
- [ ] SPI接口已启用
- [ ] GPIO权限配置正确
- [ ] 连接检测脚本通过

## 📸 连接参考图片

> 💡 **提示：** 建议在连接完成后拍照记录，便于后续维护参考。

### 标准连接示例

```
实际连接图片应放置在：
docs/assets/images/hardware-connection/
├── rpi4-epaper-2.7-connection.jpg
├── rpi5-epaper-4.2-connection.jpg
└── gpio-pinout-reference.png
```

---

**下一步：** [软件安装配置](03-software-installation.md)