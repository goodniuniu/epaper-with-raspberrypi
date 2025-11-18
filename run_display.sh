#!/bin/bash

# E-paper Weather & Poetry Display Runner
# This script sets up the environment and runs the display application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🖥️  E-paper Weather & Poetry Display${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Starting e-paper display application...${NC}"
echo

# Check if we're in the right directory
if [ ! -f "src/main_with_display.py" ]; then
    echo -e "${RED}❌ Error: main_with_display.py not found${NC}"
    echo -e "${YELLOW}Please run this script from the project root directory${NC}"
    exit 1
fi

# Set up Python path
export PYTHONPATH="$HOME/e-Paper/RaspberryPi_JetsonNano/python/lib:$PYTHONPATH"
echo -e "${GREEN}✅ Python path configured${NC}"

# Check if e-paper library exists
if [ ! -d "$HOME/e-Paper" ]; then
    echo -e "${YELLOW}⚠️  Waveshare e-paper library not found${NC}"
    echo -e "${YELLOW}Installing it now...${NC}"

    cd ~ && git clone https://github.com/waveshare/e-Paper.git
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ E-paper library installed${NC}"
    else
        echo -e "${RED}❌ Failed to install e-paper library${NC}"
        exit 1
    fi
    cd - > /dev/null
fi

# Check if Chinese fonts are installed
if [ ! -f "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc" ]; then
    echo -e "${YELLOW}⚠️  Chinese fonts not found${NC}"
    echo -e "${YELLOW}Installing them now...${NC}"

    sudo apt-get update
    sudo apt-get install -y fonts-wqy-zenhei fonts-wqy-microhei
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Chinese fonts installed${NC}"
    else
        echo -e "${RED}❌ Failed to install Chinese fonts${NC}"
        echo -e "${YELLOW}The application will run with basic fonts only${NC}"
    fi
fi

# Check config file
if [ ! -f "config.ini" ]; then
    echo -e "${RED}❌ Error: config.ini not found${NC}"
    echo -e "${YELLOW}Please create config.ini with your API keys${NC}"
    echo -e "${YELLOW}Example:${NC}"
    echo "[DEFAULT]"
    echo "WEATHER_API_KEY = your_weather_api_key"
    echo "CITY_API_KEY = YourCityName"
    echo "POEM_TOKEN_API_URL = https://v2.jinrishici.com/token"
    echo "DAILY_POEM_API_URL = https://v2.jinrishici.com/sentence"
    echo
    exit 1
fi

# Change to src directory
cd src

echo -e "${GREEN}🚀 Running e-paper display application...${NC}"
echo -e "${BLUE}Press Ctrl+C to stop${NC}"
echo

# Run the application
python main_with_display.py

# Check exit status
if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}✅ Application completed successfully${NC}"
else
    echo
    echo -e "${RED}❌ Application failed${NC}"
    echo -e "${YELLOW}Check src/epaper_app.log for error details${NC}"
fi

echo -e "${GREEN}👋 Goodbye!${NC}"