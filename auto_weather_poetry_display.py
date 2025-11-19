#!/usr/bin/env python3
"""
自动运行的天气+诗歌显示程序
Auto Weather & Poetry Display - Continuous running version
Optimized for long poems with intelligent selection
"""

import sys
import os
import time
import logging
import requests
import socket
import netifaces
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/home/admin/Github/epaper-with-raspberrypi/src/auto_display.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Set up Python path
libdir = "/home/admin/Downloads/e-Paper/RaspberryPi_JetsonNano/python/lib"
if os.path.exists(libdir):
    sys.path.insert(0, libdir)
    logger.info(f"✅ Added {libdir} to Python path")

# Famous poem selections for truncation
FAMOUS_POEM_SELECTIONS = {
    "春晓": "春眠不觉晓，处处闻啼鸟。",
    "静夜思": "床前明月光，疑是地上霜。",
    "登鹳雀楼": "白日依山尽，黄河入海流。",
    "悯农": "锄禾日当午，汗滴禾下土。",
    "咏鹅": "鹅鹅鹅，曲项向天歌。",
    "回乡偶书": "少小离家老大回，乡音无改鬓毛衰。",
    "清明": "清明时节雨纷纷，路上行人欲断魂。",
    "相思": "红豆生南国，春来发几枝。",
    "江雪": "千山鸟飞绝，万径人踪灭。",
    "枫桥夜泊": "月落乌啼霜满天，江枫渔火对愁眠。"
}

class OptimizedDisplayManager:
    """优化的显示管理器"""

    def __init__(self):
        self.epd = None
        self.fonts = None
        self.weather_api_key = "28962db3791a4792b4c90923241402"
        self.city = "Guangzhou"
        self.poem_token_file = "/home/admin/Github/epaper-with-raspberrypi/data/token.txt"

    def load_fonts(self):
        """加载字体"""
        try:
            from PIL import ImageFont

            font_path = "/home/admin/Downloads/e-Paper/RaspberryPi_JetsonNano/python/pic/Font.ttc"
            if os.path.exists(font_path):
                self.fonts = {
                    'title': ImageFont.truetype(font_path, 22),
                    'medium': ImageFont.truetype(font_path, 18),
                    'small': ImageFont.truetype(font_path, 14),
                    'tiny': ImageFont.truetype(font_path, 12)
                }
                logger.info(f"✅ Loaded fonts: {font_path}")
                return True
            else:
                from PIL import ImageFont
                self.fonts = {
                    'title': ImageFont.load_default(),
                    'medium': ImageFont.load_default(),
                    'small': ImageFont.load_default(),
                    'tiny': ImageFont.load_default()
                }
                logger.warning("⚠️ Using default fonts")
                return True

        except Exception as e:
            logger.error(f"❌ Font loading failed: {e}")
            return False

    def initialize_display(self):
        """初始化显示"""
        try:
            from waveshare_epd import epd3in52

            self.epd = epd3in52.EPD()
            self.epd.init()

            # 初始清屏
            self.epd.display_NUM(self.epd.WHITE)
            self.epd.lut_GC()
            self.epd.refresh()
            time.sleep(2)

            logger.info("✅ Display initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Display initialization failed: {e}")
            return False

    def fetch_weather_data(self):
        """获取天气数据"""
        try:
            url = f"http://api.weatherapi.com/v1/current.json?key={self.weather_api_key}&q={self.city}&aqi=no"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                weather_data = response.json()
                logger.info(f"✅ Weather data fetched: {weather_data['location']['name']} - {weather_data['current']['temp_c']}°C")
                return weather_data
            else:
                logger.warning(f"⚠️ Weather API returned {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Weather fetch failed: {e}")
            return None

    def get_device_ip(self):
        """获取设备IP地址，优先WiFi"""
        try:
            # 首先尝试获取WiFi IP
            wifi_interfaces = ['wlan0', 'wlp2s0', 'wlan1']
            for interface in wifi_interfaces:
                if interface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr_info in addrs[netifaces.AF_INET]:
                            ip = addr_info['addr']
                            if ip and not ip.startswith('127.') and not ip.startswith('169.254.'):
                                logger.info(f"✅ WiFi IP found: {ip} from {interface}")
                                return ip

            # 如果没有WiFi，尝试以太网
            eth_interfaces = ['eth0', 'enp0s3', 'enp2s0', 'eth1']
            for interface in eth_interfaces:
                if interface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr_info in addrs[netifaces.AF_INET]:
                            ip = addr_info['addr']
                            if ip and not ip.startswith('127.') and not ip.startswith('169.254.'):
                                logger.info(f"✅ Ethernet IP found: {ip} from {interface}")
                                return ip

            # 备用方法：socket连接外部地址
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                logger.info(f"✅ IP via socket: {ip}")
                return ip
            except Exception:
                pass

            logger.warning("⚠️ No valid IP address found")
            return "IP:获取失败"

        except ImportError:
            # 如果netifaces不可用，使用socket方法
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                logger.info(f"✅ IP via fallback socket: {ip}")
                return ip
            except Exception as e:
                logger.error(f"❌ Failed to get IP: {e}")
                return "IP:获取失败"
        except Exception as e:
            logger.error(f"❌ Failed to get IP: {e}")
            return "IP:获取失败"

    def get_poem_token(self):
        """获取诗歌token"""
        try:
            response = requests.get("https://v2.jinrishici.com/token", timeout=10)
            if response.status_code == 200:
                token = response.json().get('data')
                if token:
                    # 保存token
                    with open(self.poem_token_file, 'w') as f:
                        f.write(token)
                    logger.info("✅ New poetry token obtained and saved")
                    return token
        except Exception as e:
            logger.error(f"❌ Failed to get poetry token: {e}")
        return None

    def load_poem_token(self):
        """加载诗歌token"""
        try:
            if os.path.exists(self.poem_token_file):
                with open(self.poem_token_file, 'r') as f:
                    token = f.read().strip()
                if token:
                    return token
        except Exception as e:
            logger.error(f"❌ Failed to load poetry token: {e}")
        return None

    def fetch_poem_data(self):
        """获取诗歌数据"""
        # 先尝试加载现有token
        token = self.load_poem_token()

        # 如果没有token或token无效，获取新的
        if not token:
            token = self.get_poem_token()
            if not token:
                logger.error("❌ Failed to obtain poetry token")
                return None

        try:
            headers = {'X-User-Token': token}
            response = requests.get("https://v2.jinrishici.com/sentence", headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json().get('data', {})
                poem_data = {
                    'content': data.get('content', ''),
                    'title': data.get('origin', {}).get('title', ''),
                    'dynasty': data.get('origin', {}).get('dynasty', ''),
                    'author': data.get('origin', {}).get('author', ''),
                    'full_content': '\n'.join(data.get('origin', {}).get('content', []))
                }
                logger.info(f"✅ Poem data fetched: '{poem_data['title']}' by {poem_data['author']}")
                return poem_data
            else:
                logger.warning(f"⚠️ Poetry API returned {response.status_code}")
                # Token可能过期，重新获取
                new_token = self.get_poem_token()
                if new_token:
                    return self.fetch_poem_data()  # 重试一次
                return None

        except Exception as e:
            logger.error(f"❌ Poem fetch failed: {e}")
            return None

    def select_optimal_poem_content(self, poem_data):
        """智能选取最优的诗歌内容"""
        if not poem_data or not poem_data.get('content'):
            return "今日无诗", "", "", ""

        title = poem_data.get('title', '')
        dynasty = poem_data.get('dynasty', '')
        author = poem_data.get('author', '')
        content = poem_data.get('content', '')

        # 如果是长诗，选择最著名的几句
        if title in FAMOUS_POEM_SELECTIONS:
            logger.info(f"📜 Using famous selection for: {title}")
            return FAMOUS_POEM_SELECTIONS[title], title, dynasty, author

        # 如果内容太长，截取前两句
        if len(content) > 30:  # 超过30个字符认为较长
            lines = content.split('，')
            if len(lines) >= 2:
                selected = lines[0] + '，' + lines[1]
                logger.info(f"📜 Truncated long poem to: {selected}")
                return selected, title, dynasty, author
            else:
                selected = content[:25] + '...'
                logger.info(f"📜 Truncated poem to: {selected}")
                return selected, title, dynasty, author

        return content, title, dynasty, author

    def create_display_image(self, weather_data, poem_content, title, dynasty, author, device_ip):
        """创建显示图像"""
        try:
            from PIL import Image, ImageDraw

            # 创建白色背景图像
            image = Image.new('1', (self.epd.width, self.epd.height), 255)
            draw = ImageDraw.Draw(image)

            # 确保背景完全白色
            draw.rectangle([(0, 0), (self.epd.width, self.epd.height)], fill=255)

            y_pos = 8

            # === Header ===
            draw.text((8, y_pos), "天气与诗词", font=self.fonts['title'], fill=0)
            y_pos += 30

            # === Weather Section ===
            draw.line([(8, y_pos), (self.epd.width - 8, y_pos)], fill=0, width=1)
            y_pos += 8

            draw.text((8, y_pos), "当前天气", font=self.fonts['medium'], fill=0)
            y_pos += 22

            if weather_data:
                location = weather_data.get('location', {})
                current = weather_data.get('current', {})

                # Location
                location_text = location.get('name', 'Unknown')
                draw.text((8, y_pos), location_text, font=self.fonts['small'], fill=0)
                y_pos += 18

                # Temperature
                temp_text = f"温度: {current.get('temp_c', 'N/A')}°C"
                draw.text((8, y_pos), temp_text, font=self.fonts['small'], fill=0)
                y_pos += 18

                # Weather condition
                condition_text = f"天气: {current.get('condition', {}).get('text', 'Unknown')}"
                # 如果天气描述太长，截取
                if len(condition_text) > 20:
                    condition_text = condition_text[:18] + ".."
                draw.text((8, y_pos), condition_text, font=self.fonts['small'], fill=0)
                y_pos += 18

                # Humidity
                humidity_text = f"湿度: {current.get('humidity', 'N/A')}%"
                draw.text((8, y_pos), humidity_text, font=self.fonts['small'], fill=0)
                y_pos += 22
            else:
                draw.text((8, y_pos), "天气数据不可用", font=self.fonts['small'], fill=0)
                y_pos += 22

            # === Poetry Section ===
            draw.line([(8, y_pos), (self.epd.width - 8, y_pos)], fill=0, width=1)
            y_pos += 8

            draw.text((8, y_pos), "今日诗词", font=self.fonts['medium'], fill=0)
            y_pos += 22

            # Title and dynasty (if available)
            if title:
                try:
                    title_text = f"《{title}》"
                    if len(title_text) > 25:
                        title_text = title[:12] + "..》"
                    draw.text((8, y_pos), title_text, font=self.fonts['small'], fill=0)
                    y_pos += 16

                    if dynasty:
                        dynasty_text = f"({dynasty})"
                        draw.text((8, y_pos), dynasty_text, font=self.fonts['tiny'], fill=0)
                        y_pos += 16

                    if author:
                        author_text = f"— {author}"
                        if len(author_text) > 25:
                            author_text = f"— {author[:8]}.."
                        draw.text((8, y_pos), author_text, font=self.fonts['tiny'], fill=0)
                        y_pos += 20
                except Exception as e:
                    logger.warning(f"⚠️ Poetry header rendering failed: {e}")
                    y_pos += 40

            # Poem content
            if poem_content:
                try:
                    # 分行显示诗歌内容
                    lines = poem_content.split('，')
                    for i, line in enumerate(lines):
                        if line.strip() and y_pos < self.epd.height - 35:  # 留出footer空间
                            line_text = line.strip()
                            if i < len(lines) - 1:  # 不是最后一行
                                line_text += '，'

                            # 如果单行太长，适当截取
                            if len(line_text) > 22:
                                line_text = line_text[:20] + '..'

                            draw.text((8, y_pos), line_text, font=self.fonts['small'], fill=0)
                            y_pos += 16
                except Exception as e:
                    logger.warning(f"⚠️ Poetry content rendering failed: {e}")
                    draw.text((8, y_pos), "诗词显示错误", font=self.fonts['small'], fill=0)
            else:
                draw.text((8, y_pos), "诗词数据不可用", font=self.fonts['small'], fill=0)

            # === Footer ===
            footer_y = self.epd.height - 25
            draw.line([(8, footer_y), (self.epd.width - 8, footer_y)], fill=0, width=1)
            footer_y += 8

            # Left side: Update time
            timestamp = datetime.now().strftime("%m-%d %H:%M")
            draw.text((8, footer_y), f"更新: {timestamp}", font=self.fonts['tiny'], fill=0)

            # Right side: IP address
            if device_ip and device_ip != "IP:获取失败":
                ip_text = f"IP: {device_ip}"
            else:
                ip_text = "IP:获取失败"

            # 计算IP文本位置（右对齐）
            ip_width = self.fonts['tiny'].getlength(ip_text)
            ip_x = self.epd.width - ip_width - 8
            draw.text((ip_x, footer_y), ip_text, font=self.fonts['tiny'], fill=0)

            return image

        except Exception as e:
            logger.error(f"❌ Failed to create display image: {e}")
            return None

    def display_image(self, image):
        """显示图像"""
        try:
            self.epd.display(self.epd.getbuffer(image))
            self.epd.lut_GC()
            self.epd.refresh()
            logger.info("✅ Image displayed successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to display image: {e}")
            return False

    def cleanup(self):
        """清理资源"""
        if self.epd:
            try:
                self.epd.sleep()
                logger.info("✅ Display put to sleep")
            except Exception as e:
                logger.error(f"❌ Cleanup failed: {e}")

    def run_continuous(self):
        """持续运行主循环"""
        logger.info("🚀 Starting continuous display loop...")

        refresh_count = 0

        while True:
            try:
                refresh_count += 1
                logger.info(f"🔄 Refresh #{refresh_count} - {datetime.now().strftime('%H:%M:%S')}")

                # 获取天气数据
                weather_data = self.fetch_weather_data()

                # 获取诗歌数据
                poem_data = self.fetch_poem_data()
                if poem_data:
                    poem_content, title, dynasty, author = self.select_optimal_poem_content(poem_data)
                else:
                    poem_content, title, dynasty, author = "暂无诗词", "", "", ""

                # 获取设备IP地址
                device_ip = self.get_device_ip()
                logger.info(f"🖥️ Device IP: {device_ip}")

                # 创建显示图像
                image = self.create_display_image(weather_data, poem_content, title, dynasty, author, device_ip)

                if image:
                    # 保存调试图像（每10次保存一次）
                    if refresh_count % 10 == 1:
                        image.save(f'/home/admin/Github/epaper-with-raspberrypi/src/auto_display_{refresh_count}.png')

                    # 显示图像
                    if self.display_image(image):
                        logger.info(f"✅ Refresh #{refresh_count} completed successfully")
                    else:
                        logger.error(f"❌ Refresh #{refresh_count} display failed")

                # 等待5分钟
                logger.info("⏳ Waiting 5 minutes for next refresh...")
                time.sleep(300)

            except KeyboardInterrupt:
                logger.info("🛑 User interrupted, shutting down...")
                break
            except Exception as e:
                logger.error(f"❌ Error in refresh #{refresh_count}: {e}")
                # 等待30秒后重试
                time.sleep(30)

def main():
    """主函数"""
    print("🌤️ 自动天气+诗歌显示程序")
    print("=" * 50)
    print("程序将每5分钟自动刷新一次")
    print("按 Ctrl+C 停止程序")
    print("=" * 50)

    display = OptimizedDisplayManager()

    try:
        # 初始化
        if not display.load_fonts():
            logger.error("❌ Failed to load fonts, exiting")
            return False

        if not display.initialize_display():
            logger.error("❌ Failed to initialize display, exiting")
            return False

        # 开始持续运行
        display.run_continuous()

    except Exception as e:
        logger.error(f"❌ Main loop failed: {e}")
        return False
    finally:
        display.cleanup()
        logger.info("👋 Program ended")

    return True

if __name__ == "__main__":
    main()