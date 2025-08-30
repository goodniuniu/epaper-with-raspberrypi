#!/bin/bash

# 树莓派4每日单词系统安装脚本

set -e

echo "=== 树莓派4每日单词系统安装脚本 ==="
echo

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
   echo "请不要以root用户运行此脚本"
   exit 1
fi

# 检查是否在树莓派上运行
if ! grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
    echo "警告: 似乎不在树莓派上运行"
    read -p "是否继续安装? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "1. 更新系统包..."
sudo apt update && sudo apt upgrade -y

echo "2. 安装系统依赖..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-pil \
    python3-numpy \
    git \
    curl \
    wget \
    fonts-dejavu \
    fonts-dejavu-core \
    fonts-dejavu-extra

echo "3. 启用SPI接口..."
if ! grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "SPI接口已启用，重启后生效"
    NEED_REBOOT=1
else
    echo "SPI接口已启用"
fi

echo "4. 创建项目目录..."
PROJECT_DIR="$HOME/daily-word-epaper"
if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

echo "5. 创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo "6. 安装Python依赖..."
pip install --upgrade pip
pip install requests pathlib pillow numpy

# 尝试安装墨水屏库
echo "7. 安装墨水屏库..."
echo "选择墨水屏库:"
echo "1) Waveshare官方库 (推荐用于Waveshare墨水屏)"
echo "2) Luma.EPD库 (通用墨水屏库)"
echo "3) 跳过 (稍后手动安装)"

read -p "请选择 (1-3): " -n 1 -r
echo

case $REPLY in
    1)
        echo "安装Waveshare墨水屏库..."
        # 克隆Waveshare库
        if [ ! -d "e-Paper" ]; then
            git clone https://github.com/waveshare/e-Paper.git
        fi
        
        # 安装Python库
        cd e-Paper/RaspberryPi_JetsonNano/python
        sudo python3 setup.py install
        cd "$PROJECT_DIR"
        
        echo "Waveshare库安装完成"
        ;;
    2)
        echo "安装Luma.EPD库..."
        pip install luma.epd
        echo "Luma.EPD库安装完成"
        ;;
    3)
        echo "跳过墨水屏库安装"
        ;;
    *)
        echo "无效选择，跳过墨水屏库安装"
        ;;
esac

echo "8. 复制项目文件..."
# 这里假设项目文件已经存在于当前目录
# 实际部署时需要从git仓库克隆或复制文件

echo "9. 创建数据目录..."
mkdir -p data
mkdir -p logs

echo "10. 设置权限..."
chmod +x src/daily_word_rpi.py

echo "11. 创建systemd服务文件..."
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

echo "12. 创建定时任务..."
CRON_JOB="0 8,12,18 * * * cd $PROJECT_DIR && ./venv/bin/python src/daily_word_rpi.py --mode scheduled >> logs/cron.log 2>&1"

# 检查cron任务是否已存在
if ! crontab -l 2>/dev/null | grep -q "daily_word_rpi.py"; then
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "定时任务已添加 (每日8点、12点、18点更新)"
else
    echo "定时任务已存在"
fi

echo "13. 创建管理脚本..."
tee "$PROJECT_DIR/manage.sh" > /dev/null <<'EOF'
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
    clear)
        echo "清空显示..."
        source venv/bin/activate
        python src/daily_word_rpi.py --clear
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

chmod +x "$PROJECT_DIR/manage.sh"

echo "14. 运行测试..."
source venv/bin/activate
if python src/daily_word_rpi.py --test; then
    echo "✅ 测试通过"
else
    echo "❌ 测试失败，请检查配置"
fi

echo
echo "=== 安装完成 ==="
echo
echo "项目目录: $PROJECT_DIR"
echo
echo "常用命令:"
echo "  测试运行: ./manage.sh test"
echo "  手动更新: ./manage.sh update"
echo "  查看日志: ./manage.sh logs"
echo "  清空显示: ./manage.sh clear"
echo
echo "服务管理:"
echo "  启动服务: ./manage.sh start"
echo "  停止服务: ./manage.sh stop"
echo "  查看状态: ./manage.sh status"
echo "  开机自启: ./manage.sh enable"
echo

if [ "$NEED_REBOOT" = "1" ]; then
    echo "⚠️  需要重启系统以启用SPI接口"
    echo "   重启命令: sudo reboot"
fi

echo "🎉 安装完成！"