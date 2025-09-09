#!/bin/bash
# 每日单词墨水屏显示系统 - 管理脚本
# 提供系统的启动、停止、监控等功能

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
SERVICE_NAME="daily-word"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查项目目录
check_project_dir() {
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "项目目录不存在: $PROJECT_DIR"
        exit 1
    fi
    cd "$PROJECT_DIR"
}

# 检查虚拟环境
check_venv() {
    if [ ! -d "venv" ]; then
        log_error "虚拟环境不存在，请重新安装系统"
        exit 1
    fi
}

# 激活虚拟环境
activate_venv() {
    source venv/bin/activate
}

# 检查服务状态
check_service_status() {
    if systemctl is-active --quiet $SERVICE_NAME; then
        return 0  # 服务运行中
    else
        return 1  # 服务未运行
    fi
}

# 启动服务
start_service() {
    log_info "启动 $SERVICE_NAME 服务..."
    
    if check_service_status; then
        log_warning "服务已在运行中"
        return 0
    fi
    
    sudo systemctl start $SERVICE_NAME
    
    # 等待服务启动
    sleep 3
    
    if check_service_status; then
        log_success "服务启动成功"
    else
        log_error "服务启动失败"
        log_info "查看详细错误信息:"
        sudo systemctl status $SERVICE_NAME
        return 1
    fi
}

# 停止服务
stop_service() {
    log_info "停止 $SERVICE_NAME 服务..."
    
    if ! check_service_status; then
        log_warning "服务未在运行"
        return 0
    fi
    
    sudo systemctl stop $SERVICE_NAME
    
    # 等待服务停止
    sleep 2
    
    if ! check_service_status; then
        log_success "服务停止成功"
    else
        log_error "服务停止失败"
        return 1
    fi
}

# 重启服务
restart_service() {
    log_info "重启 $SERVICE_NAME 服务..."
    
    sudo systemctl restart $SERVICE_NAME
    
    # 等待服务重启
    sleep 5
    
    if check_service_status; then
        log_success "服务重启成功"
    else
        log_error "服务重启失败"
        sudo systemctl status $SERVICE_NAME
        return 1
    fi
}

# 查看服务状态
show_status() {
    log_info "查看系统状态..."
    
    echo "===========================================" 
    echo "📊 每日单词系统状态"
    echo "==========================================="
    
    # 服务状态
    if check_service_status; then
        echo -e "🔧 服务状态: ${GREEN}运行中${NC}"
    else
        echo -e "🔧 服务状态: ${RED}已停止${NC}"
    fi
    
    # 系统资源
    if command -v python3 &> /dev/null; then
        activate_venv
        python3 -c "
import psutil
print(f'💻 CPU使用率: {psutil.cpu_percent(interval=1):.1f}%')
print(f'🧠 内存使用率: {psutil.virtual_memory().percent:.1f}%')
print(f'💾 磁盘使用率: {psutil.disk_usage(\"/\").percent:.1f}%')

# CPU温度
try:
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        temp = int(f.read()) / 1000.0
        print(f'🌡️ CPU温度: {temp:.1f}°C')
except:
    pass
"
    fi
    
    # 网络连接
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        echo -e "🌐 网络连接: ${GREEN}正常${NC}"
    else
        echo -e "🌐 网络连接: ${RED}异常${NC}"
    fi
    
    # 最后更新时间
    if [ -f "data/daily_word.log" ]; then
        LAST_UPDATE=$(tail -1 data/daily_word.log | cut -d' ' -f1-2 2>/dev/null || echo "未知")
        echo "🕐 最后更新: $LAST_UPDATE"
    fi
    
    echo "==========================================="
}

# 启用开机自启
enable_autostart() {
    log_info "启用开机自启..."
    
    sudo systemctl enable $SERVICE_NAME
    
    if systemctl is-enabled --quiet $SERVICE_NAME; then
        log_success "开机自启已启用"
    else
        log_error "开机自启启用失败"
        return 1
    fi
}

# 禁用开机自启
disable_autostart() {
    log_info "禁用开机自启..."
    
    sudo systemctl disable $SERVICE_NAME
    
    if ! systemctl is-enabled --quiet $SERVICE_NAME; then
        log_success "开机自启已禁用"
    else
        log_error "开机自启禁用失败"
        return 1
    fi
}

# 手动更新显示
manual_update() {
    log_info "手动更新显示内容..."
    
    check_venv
    activate_venv
    
    if python3 src/daily_word_rpi.py --mode once; then
        log_success "显示内容更新成功"
    else
        log_error "显示内容更新失败"
        return 1
    fi
}

# 运行测试
run_test() {
    log_info "运行系统测试..."
    
    check_venv
    activate_venv
    
    echo "===========================================" 
    echo "🧪 系统测试报告"
    echo "==========================================="
    
    # 测试Python环境
    echo "🐍 Python环境测试:"
    if python3 -c "import sys; print(f'  版本: {sys.version.split()[0]}')" 2>/dev/null; then
        echo -e "  状态: ${GREEN}正常${NC}"
    else
        echo -e "  状态: ${RED}异常${NC}"
    fi
    
    # 测试依赖包
    echo "📦 依赖包测试:"
    if python3 -c "import requests, PIL, psutil; print('  核心包: 正常')" 2>/dev/null; then
        echo -e "  状态: ${GREEN}正常${NC}"
    else
        echo -e "  状态: ${RED}异常${NC}"
    fi
    
    # 测试GPIO
    echo "🔌 硬件接口测试:"
    if python3 -c "import RPi.GPIO, spidev; print('  GPIO/SPI: 正常')" 2>/dev/null; then
        echo -e "  状态: ${GREEN}正常${NC}"
    else
        echo -e "  状态: ${YELLOW}警告${NC} (可能需要重启)"
    fi
    
    # 测试网络连接
    echo "🌐 网络连接测试:"
    if python3 -c "
import requests
try:
    response = requests.get('https://api.quotable.io/random', timeout=5)
    print('  API连接: 正常')
except:
    print('  API连接: 异常')
" 2>/dev/null; then
        echo -e "  状态: ${GREEN}正常${NC}"
    else
        echo -e "  状态: ${YELLOW}警告${NC}"
    fi
    
    # 运行程序测试
    echo "🎯 程序功能测试:"
    if python3 src/daily_word_rpi.py --test 2>/dev/null; then
        echo -e "  状态: ${GREEN}正常${NC}"
    else
        echo -e "  状态: ${RED}异常${NC}"
    fi
    
    echo "==========================================="
}

# 清空显示
clear_display() {
    log_info "清空墨水屏显示..."
    
    check_venv
    activate_venv
    
    if python3 src/daily_word_rpi.py --clear; then
        log_success "显示已清空"
    else
        log_error "清空显示失败"
        return 1
    fi
}

# 查看日志
show_logs() {
    log_info "查看系统日志..."
    
    if [ -f "data/daily_word.log" ]; then
        echo "===========================================" 
        echo "📝 应用日志 (最近20行)"
        echo "==========================================="
        tail -20 data/daily_word.log
        echo
    fi
    
    echo "===========================================" 
    echo "📝 系统服务日志 (最近10行)"
    echo "==========================================="
    sudo journalctl -u $SERVICE_NAME -n 10 --no-pager
    
    echo
    log_info "实时日志监控 (按Ctrl+C退出):"
    tail -f data/daily_word.log 2>/dev/null || sudo journalctl -u $SERVICE_NAME -f
}

# 系统诊断
run_diagnosis() {
    log_info "运行系统诊断..."
    
    if [ -f "scripts/diagnose.py" ]; then
        check_venv
        activate_venv
        python3 scripts/diagnose.py
    else
        log_error "诊断脚本不存在"
        return 1
    fi
}

# 自动修复
auto_fix() {
    log_info "运行自动修复..."
    
    if [ -f "scripts/auto_fix.py" ]; then
        check_venv
        activate_venv
        python3 scripts/auto_fix.py
    else
        log_error "自动修复脚本不存在"
        return 1
    fi
}

# 系统备份
backup_system() {
    log_info "备份系统..."
    
    if [ -f "scripts/backup.sh" ]; then
        ./scripts/backup.sh
    else
        log_error "备份脚本不存在"
        return 1
    fi
}

# 显示帮助信息
show_help() {
    echo "==========================================="
    echo "🔧 每日单词系统管理脚本"
    echo "==========================================="
    echo
    echo "用法: $0 <命令>"
    echo
    echo "服务管理:"
    echo "  start      启动服务"
    echo "  stop       停止服务"
    echo "  restart    重启服务"
    echo "  status     查看状态"
    echo "  enable     启用开机自启"
    echo "  disable    禁用开机自启"
    echo
    echo "内容管理:"
    echo "  update     手动更新显示内容"
    echo "  clear      清空墨水屏显示"
    echo "  test       运行系统测试"
    echo
    echo "日志和诊断:"
    echo "  logs       查看系统日志"
    echo "  diagnose   运行系统诊断"
    echo "  fix        运行自动修复"
    echo
    echo "维护操作:"
    echo "  backup     备份系统"
    echo "  help       显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0 start     # 启动服务"
    echo "  $0 update    # 更新显示"
    echo "  $0 logs      # 查看日志"
    echo
}

# 主函数
main() {
    # 检查项目目录
    check_project_dir
    
    # 处理命令
    case "$1" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            show_status
            ;;
        enable)
            enable_autostart
            ;;
        disable)
            disable_autostart
            ;;
        update)
            manual_update
            ;;
        test)
            run_test
            ;;
        clear)
            clear_display
            ;;
        logs)
            show_logs
            ;;
        diagnose)
            run_diagnosis
            ;;
        fix)
            auto_fix
            ;;
        backup)
            backup_system
            ;;
        help|--help|-h)
            show_help
            ;;
        "")
            log_error "请指定命令"
            show_help
            exit 1
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"