#!/bin/bash

# 天气+诗歌显示服务管理脚本
# Weather & Poetry Display Service Management Script

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

case "$1" in
    start)
        echo -e "${BLUE}🚀 Starting Weather & Poetry Display Service...${NC}"
        sudo systemctl start weather-poetry-display.service
        ;;
    stop)
        echo -e "${YELLOW}⏹️ Stopping Weather & Poetry Display Service...${NC}"
        sudo systemctl stop weather-poetry-display.service
        ;;
    restart)
        echo -e "${YELLOW}🔄 Restarting Weather & Poetry Display Service...${NC}"
        sudo systemctl restart weather-poetry-display.service
        ;;
    status)
        echo -e "${BLUE}📊 Weather & Poetry Display Service Status:${NC}"
        sudo systemctl status weather-poetry-display.service
        ;;
    logs)
        echo -e "${BLUE}📋 Recent logs:${NC}"
        tail -20 /home/admin/Github/epaper-with-raspberrypi/src/auto_display.log
        ;;
    enable)
        echo -e "${GREEN}✅ Enabling Weather & Poetry Display Service (auto-start on boot)...${NC}"
        sudo systemctl enable weather-poetry-display.service
        ;;
    disable)
        echo -e "${RED}❌ Disabling Weather & Poetry Display Service...${NC}"
        sudo systemctl disable weather-poetry-display.service
        ;;
    *)
        echo -e "${GREEN}Weather & Poetry Display Service Manager${NC}"
        echo "Usage: $0 {start|stop|restart|status|logs|enable|disable}"
        echo
        echo "Commands:"
        echo "  start   - Start the service"
        echo "  stop    - Stop the service"
        echo "  restart - Restart the service"
        echo "  status  - Show service status"
        echo "  logs    - Show recent logs"
        echo "  enable  - Enable auto-start on boot"
        echo "  disable - Disable auto-start on boot"
        ;;
esac