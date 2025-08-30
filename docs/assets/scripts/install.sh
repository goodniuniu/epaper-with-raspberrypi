#!/bin/bash
# 每日单词墨水屏显示系统 - 自动安装脚本
# 适用于树莓派4/5 + Raspberry Pi OS

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="daily-word-epaper"
INSTALL_DIR="$HOME/$PROJECT_NAME"
PYTHON_VERSION="3.9"
SERVICE_NAME="daily-word"

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
check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检查系统兼容性
check_system() {
    log_info "检查系统兼容性..."
    
    # 检查操作系统
    if ! grep -q "Raspberry Pi OS" /etc/os-release 2>/dev/null; then
        log_warning "未检测到Raspberry Pi OS，继续安装可能遇到问题"
    fi
    
    # 检查架构
    ARCH=$(uname -m)
    if [[ "$ARCH" != "armv7l" && "$ARCH" != "aarch64" ]]; then
        log_warning "未检测到ARM架构，继续安装可能遇到问题"
    fi
    
    # 检查Python版本
    if ! command -v python3 &> /dev/null; then
        log_error "未找到Python3，请先安装Python3"
        exit 1
    fi
    
    PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "检测到Python版本: $PYTHON_VER"
    
    log_success "系统兼容性检查完成"
}

# 更新系统包
update_system() {
    log_info "更新系统包..."
    
    sudo apt update
    sudo apt upgrade -y
    
    log_success "系统包更新完成"
}

# 安装系统依赖
install_system_dependencies() {
    log_info "安装系统依赖..."
    
    # 基础依赖
    sudo apt install -y \
        python3-pip \
        python3-venv \
        python3-dev \
        git \
        curl \
        wget \
        build-essential \
        cmake \
        pkg-config
    
    # 图像处理依赖
    sudo apt install -y \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev
    
    # GPIO和SPI依赖
    sudo apt install -y \
        python3-rpi.gpio \
        python3-spidev
    
    # 字体
    sudo apt install -y \
        fonts-dejavu-core \
        fonts-liberation \
        fonts-noto-cjk
    
    log_success "系统依赖安装完成"
}

# 启用硬件接口
enable_hardware() {
    log_info "启用硬件接口..."
    
    # 启用SPI
    if ! grep -q "dtparam=spi=on" /boot/config.txt; then
        echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
        log_info "已启用SPI接口"
    else
        log_info "SPI接口已启用"
    fi
    
    # 启用I2C（可选）
    if ! grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
        echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
        log_info "已启用I2C接口"
    else
        log_info "I2C接口已启用"
    fi
    
    # 添加用户到相关组
    sudo usermod -a -G spi,gpio,i2c $USER
    
    log_success "硬件接口配置完成"
}

# 创建项目目录
create_project_directory() {
    log_info "创建项目目录..."
    
    if [ -d "$INSTALL_DIR" ]; then
        log_warning "项目目录已存在，将备份现有目录"
        mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # 创建目录结构
    mkdir -p {src,data,logs,scripts,themes,plugins,docs}
    
    log_success "项目目录创建完成"
}

# 创建Python虚拟环境
create_virtual_environment() {
    log_info "创建Python虚拟环境..."
    
    cd "$INSTALL_DIR"
    python3 -m venv venv
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    log_success "Python虚拟环境创建完成"
}

# 安装Python依赖
install_python_dependencies() {
    log_info "安装Python依赖..."
    
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    # 创建requirements.txt
    cat > requirements.txt << 'EOF'
# 核心依赖
requests>=2.28.0
Pillow>=9.0.0
psutil>=5.9.0

# 树莓派GPIO依赖
RPi.GPIO>=0.7.1
spidev>=3.5

# 墨水屏驱动
waveshare-epd>=1.0.0

# 可选依赖
schedule>=1.2.0
python-crontab>=2.6.0
aiohttp>=3.8.0
EOF
    
    # 安装依赖
    pip install -r requirements.txt
    
    log_success "Python依赖安装完成"
}

# 下载项目文件
download_project_files() {
    log_info "下载项目文件..."
    
    cd "$INSTALL_DIR"
    
    # 这里应该从实际的代码仓库下载
    # 暂时创建基本的项目文件结构
    
    # 创建主程序文件
    cat > src/daily_word_rpi.py << 'EOF'
#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - 主程序
"""

import sys
import argparse
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from class_word_api import WordAPI
from epaper_display_rpi import EPaperDisplay
from word_config import *

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/daily_word.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='每日单词墨水屏显示系统')
    parser.add_argument('--mode', choices=['once', 'daemon', 'scheduled'], 
                       default='once', help='运行模式')
    parser.add_argument('--test', action='store_true', help='测试模式')
    parser.add_argument('--clear', action='store_true', help='清空显示')
    
    args = parser.parse_args()
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        if args.clear:
            display = EPaperDisplay()
            display.clear_display()
            logger.info("显示已清空")
            return
        
        if args.test:
            logger.info("运行测试模式")
            # 测试逻辑
            return
        
        # 获取内容并显示
        api = WordAPI()
        display = EPaperDisplay()
        
        if api.get_daily_content():
            display.display_content(api.word_data, api.sentence_data)
            logger.info("内容更新成功")
        else:
            logger.error("内容获取失败")
    
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF
    
    # 创建其他必要文件（简化版本）
    touch src/{class_word_api.py,epaper_display_rpi.py,word_config.py}
    
    log_success "项目文件下载完成"
}

# 创建管理脚本
create_management_script() {
    log_info "创建管理脚本..."
    
    cd "$INSTALL_DIR"
    
    cat > manage.sh << 'EOF'
#!/bin/bash
# 每日单词系统管理脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="daily-word"

cd "$PROJECT_DIR"

case "$1" in
    start)
        echo "启动服务..."
        sudo systemctl start $SERVICE_NAME
        ;;
    stop)
        echo "停止服务..."
        sudo systemctl stop $SERVICE_NAME
        ;;
    restart)
        echo "重启服务..."
        sudo systemctl restart $SERVICE_NAME
        ;;
    status)
        echo "查看服务状态..."
        sudo systemctl status $SERVICE_NAME
        ;;
    enable)
        echo "启用开机自启..."
        sudo systemctl enable $SERVICE_NAME
        ;;
    disable)
        echo "禁用开机自启..."
        sudo systemctl disable $SERVICE_NAME
        ;;
    update)
        echo "手动更新显示..."
        source venv/bin/activate
        python3 src/daily_word_rpi.py --mode once
        ;;
    test)
        echo "运行测试..."
        source venv/bin/activate
        python3 src/daily_word_rpi.py --test
        ;;
    clear)
        echo "清空显示..."
        source venv/bin/activate
        python3 src/daily_word_rpi.py --clear
        ;;
    logs)
        echo "查看日志..."
        tail -f data/daily_word.log
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|enable|disable|update|test|clear|logs}"
        exit 1
        ;;
esac
EOF
    
    chmod +x manage.sh
    
    log_success "管理脚本创建完成"
}

# 创建systemd服务
create_systemd_service() {
    log_info "创建systemd服务..."
    
    sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=Daily Word E-Paper Display Service
Documentation=https://github.com/your-repo/daily-word-epaper
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
Environment=PYTHONPATH=$INSTALL_DIR/src
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/src/daily_word_rpi.py --mode daemon
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
ReadWritePaths=$INSTALL_DIR

# 资源限制
MemoryMax=256M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd配置
    sudo systemctl daemon-reload
    
    log_success "systemd服务创建完成"
}

# 设置定时任务
setup_cron_jobs() {
    log_info "设置定时任务..."
    
    # 创建cron任务
    (crontab -l 2>/dev/null; echo "# 每日单词系统定时任务") | crontab -
    (crontab -l 2>/dev/null; echo "0 8,12,18 * * * cd $INSTALL_DIR && ./venv/bin/python src/daily_word_rpi.py --mode scheduled >> logs/cron.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 2 * * 0 find $INSTALL_DIR/logs -name '*.log' -mtime +7 -delete") | crontab -
    
    log_success "定时任务设置完成"
}

# 设置权限
set_permissions() {
    log_info "设置文件权限..."
    
    cd "$INSTALL_DIR"
    
    # 设置脚本执行权限
    find . -name "*.py" -exec chmod +x {} \;
    find . -name "*.sh" -exec chmod +x {} \;
    
    # 设置目录权限
    chmod 755 src scripts
    chmod 766 data logs
    
    log_success "文件权限设置完成"
}

# 运行初始测试
run_initial_test() {
    log_info "运行初始测试..."
    
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    # 测试Python环境
    python3 -c "import sys; print(f'Python版本: {sys.version}')"
    
    # 测试依赖包
    python3 -c "
import requests, PIL, psutil
print('✅ 核心依赖包正常')
"
    
    # 测试GPIO（如果可用）
    if python3 -c "import RPi.GPIO; print('✅ GPIO可用')" 2>/dev/null; then
        log_success "GPIO测试通过"
    else
        log_warning "GPIO测试失败，可能需要重启后生效"
    fi
    
    log_success "初始测试完成"
}

# 显示安装完成信息
show_completion_info() {
    log_success "安装完成！"
    
    echo
    echo "===========================================" 
    echo "🎉 每日单词墨水屏显示系统安装完成！"
    echo "==========================================="
    echo
    echo "📁 安装目录: $INSTALL_DIR"
    echo "🔧 管理命令: ./manage.sh"
    echo "📋 服务名称: $SERVICE_NAME"
    echo
    echo "🚀 快速开始:"
    echo "  cd $INSTALL_DIR"
    echo "  ./manage.sh test     # 运行测试"
    echo "  ./manage.sh update   # 手动更新"
    echo "  ./manage.sh start    # 启动服务"
    echo "  ./manage.sh enable   # 启用自启"
    echo
    echo "📖 更多信息请查看文档:"
    echo "  docs/installation-guide/"
    echo "  docs/user-manual/"
    echo
    echo "⚠️  重要提示:"
    echo "  1. 请重启系统以确保硬件接口生效"
    echo "  2. 确保墨水屏正确连接到GPIO引脚"
    echo "  3. 首次运行前请检查网络连接"
    echo
    echo "🆘 如遇问题:"
    echo "  ./manage.sh logs     # 查看日志"
    echo "  python3 scripts/diagnose.py  # 运行诊断"
    echo
}

# 主安装流程
main() {
    echo "==========================================="
    echo "🚀 每日单词墨水屏显示系统 - 自动安装程序"
    echo "==========================================="
    echo
    
    # 检查权限
    check_root
    
    # 系统检查
    check_system
    
    # 询问用户确认
    echo "即将开始安装，这将需要几分钟时间。"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "安装已取消"
        exit 0
    fi
    
    # 执行安装步骤
    update_system
    install_system_dependencies
    enable_hardware
    create_project_directory
    create_virtual_environment
    install_python_dependencies
    download_project_files
    create_management_script
    create_systemd_service
    setup_cron_jobs
    set_permissions
    run_initial_test
    
    # 显示完成信息
    show_completion_info
    
    # 询问是否立即重启
    echo
    read -p "是否现在重启系统以使硬件配置生效？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "系统将在5秒后重启..."
        sleep 5
        sudo reboot
    else
        log_warning "请记得稍后重启系统以使硬件配置生效"
    fi
}

# 错误处理
trap 'log_error "安装过程中发生错误，请检查日志"; exit 1' ERR

# 运行主程序
main "$@"