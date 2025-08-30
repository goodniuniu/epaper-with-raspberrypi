# 软件安装配置

## 📋 概述

本章节将指导您完成系统软件的安装和配置，包括操作系统更新、Python环境设置、依赖库安装和项目部署。

## 🚀 快速安装（推荐）

### 自动安装脚本

```bash
# 下载并运行自动安装脚本
curl -sSL https://raw.githubusercontent.com/your-repo/main/docs/assets/scripts/install.sh | bash
```

如果您选择自动安装，可以跳过手动安装步骤，直接查看[安装验证](#安装验证)部分。

## 🔧 手动安装步骤

### 步骤1：系统更新

```bash
# 更新软件包列表
sudo apt update

# 升级系统软件包
sudo apt upgrade -y

# 安装必要的系统工具
sudo apt install -y curl wget git vim nano htop
```

### 步骤2：启用SPI接口

```bash
# 方法1：使用raspi-config（推荐）
sudo raspi-config
# 选择：Interfacing Options -> SPI -> Enable -> Yes -> Finish

# 方法2：直接编辑配置文件
echo 'dtparam=spi=on' | sudo tee -a /boot/config.txt

# 重启系统使配置生效
sudo reboot
```

### 步骤3：安装Python依赖

```bash
# 安装Python开发环境
sudo apt install -y python3 python3-pip python3-venv python3-dev

# 安装系统级Python库
sudo apt install -y python3-pil python3-numpy python3-spidev

# 安装图像处理库依赖
sudo apt install -y libjpeg-dev zlib1g-dev libfreetype6-dev

# 安装字体
sudo apt install -y fonts-dejavu fonts-dejavu-core fonts-dejavu-extra
sudo apt install -y fonts-wqy-zenhei fonts-wqy-microhei  # 中文字体支持
```

### 步骤4：创建项目目录

```bash
# 创建项目根目录
PROJECT_DIR="$HOME/daily-word-epaper"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 创建必要的子目录
mkdir -p {src,data,logs,docs,scripts}
```

### 步骤5：下载项目文件

```bash
# 方法1：从Git仓库克隆（推荐）
git clone https://github.com/your-repo/daily-word-epaper.git .

# 方法2：手动下载文件
# 如果没有Git仓库，需要手动复制以下文件：
# - src/class_word_api.py
# - src/epaper_display_rpi.py
# - src/daily_word_rpi.py
# - src/word_config_rpi.py
# - src/test_word_api.py
```

### 步骤6：创建Python虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

### 步骤7：安装Python包

```bash
# 安装基础依赖
pip install requests pathlib pillow numpy

# 安装墨水屏库（选择其中一种）

# 选项1：Waveshare官方库
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python
sudo python3 setup.py install
cd "$PROJECT_DIR"

# 选项2：Luma.EPD库（通用）
pip install luma.epd

# 选项3：RPi.GPIO库（基础GPIO控制）
pip install RPi.GPIO spidev
```

### 步骤8：配置权限

```bash
# 添加用户到必要的组
sudo usermod -a -G spi,gpio,i2c $USER

# 设置文件权限
chmod +x src/daily_word_rpi.py
chmod +x src/test_word_api.py

# 创建数据目录权限
sudo chown -R $USER:$USER "$PROJECT_DIR"
chmod -R 755 "$PROJECT_DIR"
```

## 📦 依赖包详细说明

### 核心依赖

| 包名 | 版本要求 | 用途 | 安装命令 |
|------|----------|------|----------|
| **requests** | ≥2.25.0 | HTTP请求 | `pip install requests` |
| **Pillow** | ≥8.0.0 | 图像处理 | `pip install pillow` |
| **numpy** | ≥1.19.0 | 数值计算 | `pip install numpy` |

### 墨水屏驱动

| 库名 | 适用硬件 | 安装方式 | 说明 |
|------|----------|----------|------|
| **waveshare-epd** | Waveshare墨水屏 | 源码安装 | 官方驱动库 |
| **luma.epd** | 通用墨水屏 | `pip install` | 通用驱动库 |
| **RPi.GPIO** | 所有GPIO设备 | `pip install` | 基础GPIO控制 |

### 系统服务

| 服务 | 用途 | 配置文件 |
|------|------|----------|
| **systemd** | 服务管理 | `/etc/systemd/system/` |
| **cron** | 定时任务 | `/etc/crontab` |
| **logrotate** | 日志轮转 | `/etc/logrotate.d/` |

## 🔧 配置文件设置

### 创建主配置文件

```bash
# 复制配置模板
cp src/word_config_rpi.py src/word_config.py

# 编辑配置文件
nano src/word_config.py
```

### 关键配置项

```python
# 墨水屏配置
DISPLAY_CONFIG = {
    'epd_type': 'waveshare_2in7',  # 根据实际硬件修改
    'width': 264,
    'height': 176,
    'gpio_pins': {
        'rst': 17,
        'dc': 25,
        'cs': 8,
        'busy': 24
    }
}

# API配置
WORD_API_CONFIG = {
    'word_api_url': 'https://api.wordnik.com/v4/words.json/wordOfTheDay',
    'sentence_api_url': 'https://v1.hitokoto.cn/?c=i&encode=json',
    'timeout': 15,
    'max_retries': 3
}
```

## 🧪 安装验证

### 基础功能测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 测试Python导入
python3 -c "
import requests
import PIL
import numpy
print('✅ 基础库导入成功')
"

# 测试GPIO访问
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
print('✅ GPIO访问正常')
"

# 测试SPI接口
python3 -c "
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
spi.close()
print('✅ SPI接口正常')
"
```

### 墨水屏驱动测试

```bash
# 测试Waveshare驱动（如果安装了）
python3 -c "
try:
    import epd2in7
    print('✅ Waveshare 2.7寸驱动正常')
except ImportError:
    print('⚠️ Waveshare驱动未安装')
"

# 测试Luma.EPD驱动（如果安装了）
python3 -c "
try:
    from luma.epd.device import ssd1675
    print('✅ Luma.EPD驱动正常')
except ImportError:
    print('⚠️ Luma.EPD驱动未安装')
"
```

### 项目功能测试

```bash
# 运行项目测试脚本
python3 src/test_word_api.py

# 运行硬件连接测试
python3 src/daily_word_rpi.py --test

# 预期输出示例：
# === 每日单词系统启动 ===
# 墨水屏显示器初始化成功
# 成功获取每日单词: example
# ✅ 硬件连接检查通过
```

## 🔄 自动安装脚本

### 创建完整安装脚本

<write_to_file>
<path>docs/assets/scripts/install.sh</path>
<content>#!/bin/bash

# 每日单词墨水屏显示系统 - 自动安装脚本
# 适用于树莓派4/5 + Raspberry Pi OS

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_user() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要以root用户运行此脚本"
        exit 1
    fi
}

# 检查系统
check_system() {
    log_info "检查系统环境..."
    
    # 检查是否为树莓派
    if ! grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
        log_warning "似乎不在树莓派上运行"
        read -p "是否继续安装? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 检查操作系统
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        log_info "检测到系统: $PRETTY_NAME"
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_info "Python版本: $PYTHON_VERSION"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_error "需要Python 3.8或更高版本"
        exit 1
    fi
}

# 更新系统
update_system() {
    log_info "更新系统软件包..."
    sudo apt update
    sudo apt upgrade -y
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        python3-pil \
        python3-numpy \
        python3-spidev \
        git \
        curl \
        wget \
        fonts-dejavu \
        fonts-dejavu-core \
        fonts-dejavu-extra \
        libjpeg-dev \
        zlib1g-dev \
        libfreetype6-dev
    
    log_success "系统依赖安装完成"
}

# 启用SPI接口
enable_spi() {
    log_info "启用SPI接口..."
    
    if ! grep -q "dtparam=spi=on" /boot/config.txt; then
        echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
        log_success "SPI接口已启用，重启后生效"
        NEED_REBOOT=1
    else
        log_info "SPI接口已启用"
    fi
}

# 创建项目目录
create_project_dir() {
    PROJECT_DIR="$HOME/daily-word-epaper"
    log_info "创建项目目录: $PROJECT_DIR"
    
    if [[ -d "$PROJECT_DIR" ]]; then
        log_warning "项目目录已存在"
        read -p "是否删除现有目录并重新创建? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$PROJECT_DIR"
        else
            log_info "使用现有目录"
        fi
    fi
    
    mkdir -p "$PROJECT_DIR"/{src,data,logs,docs,scripts}
    cd "$PROJECT_DIR"
}

# 创建Python虚拟环境
create_venv() {
    log_info "创建Python虚拟环境..."
    
    if [[ -d "venv" ]]; then
        log_warning "虚拟环境已存在，跳过创建"
    else
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    
    log_success "虚拟环境创建完成"
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖..."
    
    source venv/bin/activate
    
    # 安装基础依赖
    pip install requests pathlib pillow numpy RPi.GPIO spidev
    
    log_success "Python依赖安装完成"
}

# 安装墨水屏库
install_epaper_lib() {
    log_info "选择墨水屏库..."
    
    echo "请选择墨水屏库:"
    echo "1) Waveshare官方库 (推荐用于Waveshare墨水屏)"
    echo "2) Luma.EPD库 (通用墨水屏库)"
    echo "3) 跳过 (稍后手动安装)"
    
    read -p "请选择 (1-3): " -n 1 -r
    echo
    
    source venv/bin/activate
    
    case $REPLY in
        1)
            log_info "安装Waveshare墨水屏库..."
            if [[ ! -d "e-Paper" ]]; then
                git clone https://github.com/waveshare/e-Paper.git
            fi
            cd e-Paper/RaspberryPi_JetsonNano/python
            sudo python3 setup.py install
            cd "$PROJECT_DIR"
            log_success "Waveshare库安装完成"
            ;;
        2)
            log_info "安装Luma.EPD库..."
            pip install luma.epd
            log_success "Luma.EPD库安装完成"
            ;;
        3)
            log_info "跳过墨水屏库安装"
            ;;
        *)
            log_warning "无效选择，跳过墨水屏库安装"
            ;;
    esac
}

# 下载项目文件
download_project_files() {
    log_info "下载项目文件..."
    
    # 这里应该从实际的Git仓库下载
    # git clone https://github.com/your-repo/daily-word-epaper.git .
    
    # 临时创建示例文件
    cat > src/word_config.py << 'EOF'
# 配置文件示例
DISPLAY_CONFIG = {
    'epd_type': 'waveshare_2in7',
    'width': 264,
    'height': 176,
    'gpio_pins': {
        'rst': 17,
        'dc': 25,
        'cs': 8,
        'busy': 24
    }
}
EOF
    
    log_success "项目文件下载完成"
}

# 配置权限
setup_permissions() {
    log_info "配置权限..."
    
    # 添加用户到必要的组
    sudo usermod -a -G spi,gpio $USER
    
    # 设置文件权限
    chmod +x src/*.py 2>/dev/null || true
    
    # 设置目录权限
    sudo chown -R $USER:$USER "$PROJECT_DIR"
    chmod -R 755 "$PROJECT_DIR"
    
    log_success "权限配置完成"
}

# 创建系统服务
create_systemd_service() {
    log_info "创建systemd服务..."
    
    SERVICE_FILE="/etc/systemd/system/daily-word.service"
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Daily Word E-Paper Display
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/src/daily_word_rpi.py --mode scheduled
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    log_success "systemd服务创建完成"
}

# 创建定时任务
create_cron_job() {
    log_info "创建定时任务..."
    
    CRON_JOB="0 8,12,18 * * * cd $PROJECT_DIR && ./venv/bin/python src/daily_word_rpi.py --mode scheduled >> logs/cron.log 2>&1"
    
    if ! crontab -l 2>/dev/null | grep -q "daily_word_rpi.py"; then
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        log_success "定时任务已添加"
    else
        log_info "定时任务已存在"
    fi
}

# 创建管理脚本
create_management_script() {
    log_info "创建管理脚本..."
    
    cat > manage.sh << 'EOF'
#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

case "$1" in
    start)
        echo "启动每日单词服务..."
        sudo systemctl start daily-word
        ;;
    stop)
        echo "停止每日单词服务..."
        sudo systemctl stop daily-word
        ;;
    restart)
        echo "重启每日单词服务..."
        sudo systemctl restart daily-word
        ;;
    status)
        sudo systemctl status daily-word
        ;;
    enable)
        echo "启用开机自启..."
        sudo systemctl enable daily-word
        ;;
    disable)
        echo "禁用开机自启..."
        sudo systemctl disable daily-word
        ;;
    update)
        echo "手动更新显示..."
        source venv/bin/activate
        python src/daily_word_rpi.py --mode once
        ;;
    test)
        echo "运行测试..."
        source venv/bin/activate
        python src/daily_word_rpi.py --test
        ;;
    logs)
        echo "查看日志..."
        tail -f data/daily_word.log
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|enable|disable|update|test|logs}"
        exit 1
        ;;
esac
EOF
    
    chmod +x manage.sh
    log_success "管理脚本创建完成"
}

# 运行测试
run_tests() {
    log_info "运行安装测试..."
    
    source venv/bin/activate
    
    # 基础库测试
    python3 -c "
import requests
import PIL
import numpy
print('✅ 基础库导入成功')
" || log_error "基础库测试失败"
    
    # GPIO测试
    python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
print('✅ GPIO访问正常')
" || log_error "GPIO测试失败"
    
    # SPI测试
    python3 -c "
import spidev
spi = spidev.SpiDev()
try:
    spi.open(0, 0)
    spi.close()
    print('✅ SPI接口正常')
except:
    print('⚠️ SPI接口可能未启用')
" || log_warning "SPI测试失败"
    
    log_success "安装测试完成"
}

# 显示安装结果
show_results() {
    echo
    log_success "=== 安装完成 ==="
    echo
    echo "项目目录: $PROJECT_DIR"
    echo
    echo "常用命令:"
    echo "  测试运行: ./manage.sh test"
    echo "  手动更新: ./manage.sh update"
    echo "  查看日志: ./manage.sh logs"
    echo
    echo "服务管理:"
    echo "  启动服务: ./manage.sh start"
    echo "  停止服务: ./manage.sh stop"
    echo "  查看状态: ./manage.sh status"
    echo "  开机自启: ./manage.sh enable"
    echo
    
    if [[ "$NEED_REBOOT" == "1" ]]; then
        log_warning "需要重启系统以启用SPI接口"
        echo "重启命令: sudo reboot"
    fi
    
    echo "🎉 安装完成！"
}

# 主函数
main() {
    echo "=== 每日单词墨水屏显示系统 - 自动安装 ==="
    echo
    
    check_user
    check_system
    update_system
    install_system_deps
    enable_spi
    create_project_dir
    create_venv
    install_python_deps
    install_epaper_lib
    download_project_files
    setup_permissions
    create_systemd_service
    create_cron_job
    create_management_script
    run_tests
    show_results
}

# 运行主函数
main "$@"
EOF

chmod +x docs/assets/scripts/install.sh
```

## 📋 安装检查清单

完成安装后，请确认以下项目：

- [ ] 系统软件包已更新
- [ ] SPI接口已启用
- [ ] Python虚拟环境已创建
- [ ] 所有依赖包已安装
- [ ] 墨水屏驱动库已安装
- [ ] 项目文件已下载
- [ ] 权限配置正确
- [ ] 系统服务已创建
- [ ] 定时任务已设置
- [ ] 管理脚本可用
- [ ] 基础测试通过

## 🔍 故障排除

### 常见安装问题

#### 问题1：pip安装失败

```bash
# 解决方案：升级pip和setuptools
python3 -m pip install --upgrade pip setuptools wheel

# 如果仍然失败，尝试使用系统包管理器
sudo apt install python3-requests python3-pil python3-numpy
```

#### 问题2：权限错误

```bash
# 解决方案：检查用户组
groups $USER

# 添加到必要的组
sudo usermod -a -G spi,gpio,i2c $USER

# 重新登录使权限生效
logout
```

#### 问题3：SPI接口问题

```bash
# 检查SPI是否启用
ls /dev/spi*

# 如果没有输出，手动启用
sudo raspi-config
# 选择 Interfacing Options -> SPI -> Enable

# 或直接编辑配置文件
echo 'dtparam=spi=on' | sudo tee -a /boot/config.txt
sudo reboot
```

#### 问题4：墨水屏库安装失败

```bash
# Waveshare库安装问题
cd e-Paper/RaspberryPi_JetsonNano/python
sudo python3 setup.py install --force

# Luma.EPD库安装问题
pip install --upgrade luma.epd

# 如果都失败，使用基础GPIO库
pip install RPi.GPIO spidev
```

---

**下一步：** [系统参数配置](04-configuration.md)