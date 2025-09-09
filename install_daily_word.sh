#!/bin/bash
# 每日单词墨水屏显示系统安装脚本
# Daily Word E-Paper Display System Installation Script

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="每日单词墨水屏显示系统"
PROJECT_VERSION="1.0.0"
INSTALL_DIR="/opt/daily-word-epaper"
SERVICE_NAME="daily-word"
USER_NAME="$SUDO_USER"

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
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        echo "请使用: sudo $0"
        exit 1
    fi
}

# 检查系统兼容性
check_system() {
    log_info "检查系统兼容性..."
    
    # 检查操作系统
    if [[ ! -f /etc/os-release ]]; then
        log_error "无法识别操作系统"
        exit 1
    fi
    
    source /etc/os-release
    log_info "检测到系统: $PRETTY_NAME"
    
    # 检查架构
    ARCH=$(uname -m)
    log_info "系统架构: $ARCH"
    
    if [[ "$ARCH" != "armv7l" && "$ARCH" != "aarch64" ]]; then
        log_warning "未在树莓派架构上测试，可能存在兼容性问题"
    fi
    
    # 检查Python版本
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_info "Python版本: $PYTHON_VERSION"
        
        # 检查Python版本是否满足要求
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
            log_success "Python版本满足要求"
        else
            log_error "需要Python 3.7或更高版本"
            exit 1
        fi
    else
        log_error "未找到Python3"
        exit 1
    fi
}

# 安装系统依赖
install_system_dependencies() {
    log_info "跳过系统依赖安装..."
    log_info "系统依赖已通过其他方式安装"
    
    # 树莓派特定依赖检查
    if [[ "$ARCH" == "armv7l" || "$ARCH" == "aarch64" ]]; then
        log_info "检查树莓派依赖..."
        # 检查SPI是否已启用
        if [[ ! -e /dev/spidev0.0 ]]; then
            log_warning "SPI接口未启用，请手动运行: raspi-config nonint do_spi 0"
        fi
    fi
    
    log_success "系统依赖检查完成"
}

# 创建安装目录
create_directories() {
    log_info "创建安装目录..."
    
    # 创建主目录
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/src"
    mkdir -p "$INSTALL_DIR/data"
    mkdir -p "$INSTALL_DIR/logs"
    mkdir -p "$INSTALL_DIR/cache"
    
    # 设置权限
    chown -R "$SUDO_USER:$SUDO_USER" "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    
    log_success "目录创建完成"
}

# 复制项目文件
copy_project_files() {
    log_info "复制项目文件..."
    
    # 获取脚本所在目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # 复制源代码
    if [[ -d "$SCRIPT_DIR/src" ]]; then
        cp -r "$SCRIPT_DIR/src"/* "$INSTALL_DIR/src/"
        log_success "源代码复制完成"
    else
        log_error "未找到src目录"
        exit 1
    fi
    
    # 复制文档
    if [[ -d "$SCRIPT_DIR/docs" ]]; then
        cp -r "$SCRIPT_DIR/docs" "$INSTALL_DIR/"
        log_success "文档复制完成"
    fi
    
    # 复制其他文件
    for file in README.md PROJECT_STRUCTURE.md DEPLOYMENT_CHECKLIST.md; do
        if [[ -f "$SCRIPT_DIR/$file" ]]; then
            cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/"
        fi
    done
    
    # 设置权限
    chown -R "$SUDO_USER:$SUDO_USER" "$INSTALL_DIR"
    chmod +x "$INSTALL_DIR/src"/*.py
    
    log_success "项目文件复制完成"
}

# 创建Python虚拟环境
create_virtual_environment() {
    log_info "创建Python虚拟环境..."
    
    # 切换到安装目录
    cd "$INSTALL_DIR"
    
    # 创建虚拟环境
    sudo -u "$USER_NAME" python3 -m venv venv
    
    # 激活虚拟环境并安装依赖
    sudo -u "$SUDO_USER" bash -c "
        source venv/bin/activate
        pip install --upgrade pip
        pip install \
            requests \
            pillow \
            pathlib \
            typing-extensions
    "
    
    # 树莓派特定依赖
    if [[ "$ARCH" == "armv7l" || "$ARCH" == "aarch64" ]]; then
        sudo -u "$SUDO_USER" bash -c "
            source venv/bin/activate
            pip install \
                RPi.GPIO \
                spidev
        "
    fi
    
    log_success "虚拟环境创建完成"
}

# 创建systemd服务
create_systemd_service() {
    log_info "创建systemd服务..."
    
    cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOF
[Unit]
Description=${PROJECT_NAME}
After=network.target
Wants=network.target

[Service]
Type=simple
User=${SUDO_USER}
Group=${SUDO_USER}
WorkingDirectory=${INSTALL_DIR}
Environment=PATH=${INSTALL_DIR}/venv/bin
ExecStart=${INSTALL_DIR}/venv/bin/python ${INSTALL_DIR}/src/daily_word_main.py --daemon
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd配置
    systemctl daemon-reload
    
    log_success "systemd服务创建完成"
}

# 创建管理脚本
create_management_script() {
    log_info "创建管理脚本..."
    
    cat > "$INSTALL_DIR/manage.sh" << 'EOF'
#!/bin/bash
# 每日单词系统管理脚本

SERVICE_NAME="daily-word"
INSTALL_DIR="/opt/daily-word-epaper"

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
        echo "服务状态:"
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
    logs)
        echo "查看日志:"
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    test)
        echo "测试系统..."
        cd $INSTALL_DIR
        ./venv/bin/python src/daily_word_test.py
        ;;
    update)
        echo "更新显示..."
        cd $INSTALL_DIR
        ./venv/bin/python src/daily_word_main.py --force
        ;;
    clear)
        echo "清空显示..."
        cd $INSTALL_DIR
        ./venv/bin/python src/daily_word_main.py --clear
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|enable|disable|logs|test|update|clear}"
        exit 1
        ;;
esac
EOF
    
    chmod +x "$INSTALL_DIR/manage.sh"
    chown "$USER_NAME:$USER_NAME" "$INSTALL_DIR/manage.sh"
    
    # 创建全局命令链接
    ln -sf "$INSTALL_DIR/manage.sh" "/usr/local/bin/daily-word"
    
    log_success "管理脚本创建完成"
}

# 运行测试
run_tests() {
    log_info "运行系统测试..."
    
    cd "$INSTALL_DIR"
    
    # 运行测试脚本
    if sudo -u "$SUDO_USER" ./venv/bin/python src/daily_word_test.py; then
        log_success "系统测试通过"
        return 0
    else
        log_warning "系统测试失败，但安装继续"
        return 1
    fi
}

# 完成安装
finish_installation() {
    log_info "完成安装配置..."
    
    # 启用服务
    systemctl enable "$SERVICE_NAME"
    
    # 创建桌面快捷方式（如果存在桌面环境）
    if [[ -d "/home/$USER_NAME/Desktop" ]]; then
        cat > "/home/$USER_NAME/Desktop/daily-word.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=每日单词
Comment=每日单词墨水屏显示系统
Exec=/usr/local/bin/daily-word test
Icon=applications-education
Terminal=true
Categories=Education;
EOF
        
        chown "$USER_NAME:$USER_NAME" "/home/$USER_NAME/Desktop/daily-word.desktop"
        chmod +x "/home/$USER_NAME/Desktop/daily-word.desktop"
    fi
    
    log_success "安装完成！"
}

# 显示安装结果
show_installation_summary() {
    echo
    echo "=" * 60
    log_success "$PROJECT_NAME 安装完成！"
    echo "=" * 60
    echo
    echo "📁 安装目录: $INSTALL_DIR"
    echo "🔧 管理命令: daily-word"
    echo "📋 服务名称: $SERVICE_NAME"
    echo
    echo "🚀 快速开始:"
    echo "  daily-word test     # 测试系统"
    echo "  daily-word start    # 启动服务"
    echo "  daily-word status   # 查看状态"
    echo "  daily-word update   # 更新显示"
    echo "  daily-word logs     # 查看日志"
    echo
    echo "📖 详细文档: $INSTALL_DIR/docs/"
    echo
    log_info "建议重启系统以确保所有配置生效"
}

# 主安装流程
main() {
    echo "=" * 60
    log_info "开始安装 $PROJECT_NAME v$PROJECT_VERSION"
    echo "=" * 60
    
    check_root
    check_system
    install_system_dependencies
    create_directories
    copy_project_files
    create_virtual_environment
    create_systemd_service
    create_management_script
    run_tests
    finish_installation
    show_installation_summary
}

# 错误处理
trap 'log_error "安装过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"