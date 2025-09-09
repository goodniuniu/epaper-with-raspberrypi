#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - 显示控制器
Daily Word E-Paper Display System - Display Controller

负责将内容渲染到墨水屏上显示
"""

import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("警告: PIL库未安装，请运行: pip install Pillow")
    sys.exit(1)

# 尝试导入墨水屏驱动
try:
    import spidev
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    print("警告: 硬件库未安装，运行在模拟模式")
    HARDWARE_AVAILABLE = False

from daily_word_config import (
    EPAPER_CONFIG, FONT_CONFIG, LAYOUT_CONFIG, THEME_CONFIG,
    SUPPORTED_EPAPER_MODELS, DEBUG_CONFIG
)

# 配置日志
logger = logging.getLogger(__name__)

class DailyWordDisplayController:
    """每日单词显示控制器"""
    
    def __init__(self):
        """初始化显示控制器"""
        self.width = EPAPER_CONFIG['width']
        self.height = EPAPER_CONFIG['height']
        self.model = EPAPER_CONFIG['model']
        
        # 获取当前主题
        self.current_theme = THEME_CONFIG['themes'][THEME_CONFIG['current_theme']]
        
        # 初始化字体
        self.fonts = self._load_fonts()
        
        # 初始化硬件
        if HARDWARE_AVAILABLE and not DEBUG_CONFIG['mock_hardware']:
            self._init_hardware()
        else:
            logger.warning("运行在模拟模式，不会实际控制硬件")
        
        logger.info(f"显示控制器初始化完成 - 型号: {self.model}, 尺寸: {self.width}x{self.height}")
    
    def _load_fonts(self) -> Dict[str, Any]:
        """加载字体"""
        fonts = {}
        font_paths = FONT_CONFIG['font_paths']
        font_sizes = FONT_CONFIG['font_sizes']
        
        try:
            # 加载不同大小的字体
            for font_type, size in font_sizes.items():
                font_path = font_paths.get('default', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
                
                # 特殊字体类型使用对应的字体文件
                if font_type in ['title', 'word'] and 'bold' in font_paths:
                    font_path = font_paths['bold']
                elif font_type in ['phonetic', 'example'] and 'mono' in font_paths:
                    font_path = font_paths['mono']
                
                try:
                    fonts[font_type] = ImageFont.truetype(font_path, size)
                    logger.debug(f"成功加载字体: {font_type} - {font_path} ({size}px)")
                except (OSError, IOError):
                    # 如果字体文件不存在，使用默认字体
                    fonts[font_type] = ImageFont.load_default()
                    logger.warning(f"字体文件不存在，使用默认字体: {font_type}")
            
            return fonts
            
        except Exception as e:
            logger.error(f"加载字体失败: {e}")
            # 返回默认字体字典
            return {key: ImageFont.load_default() for key in font_sizes.keys()}
    
    def _init_hardware(self):
        """初始化硬件"""
        try:
            # 设置GPIO模式
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # 获取GPIO引脚配置
            gpio_pins = EPAPER_CONFIG['gpio_pins']
            self.RST_PIN = gpio_pins['RST_PIN']
            self.DC_PIN = gpio_pins['DC_PIN']
            self.CS_PIN = gpio_pins['CS_PIN']
            self.BUSY_PIN = gpio_pins['BUSY_PIN']
            
            # 设置GPIO引脚
            GPIO.setup(self.RST_PIN, GPIO.OUT)
            GPIO.setup(self.DC_PIN, GPIO.OUT)
            GPIO.setup(self.CS_PIN, GPIO.OUT)
            GPIO.setup(self.BUSY_PIN, GPIO.IN)
            
            # 初始化SPI
            spi_config = EPAPER_CONFIG['spi_config']
            self.spi = spidev.SpiDev()
            self.spi.open(spi_config['bus'], spi_config['device'])
            self.spi.max_speed_hz = spi_config['max_speed_hz']
            self.spi.mode = 0b00
            
            logger.info("硬件初始化完成")
            
        except Exception as e:
            logger.error(f"硬件初始化失败: {e}")
            raise
    
    def _wait_until_idle(self):
        """等待墨水屏空闲"""
        if not HARDWARE_AVAILABLE or DEBUG_CONFIG['mock_hardware']:
            return
        
        logger.debug("等待墨水屏空闲...")
        while GPIO.input(self.BUSY_PIN) == 1:
            time.sleep(0.01)
        logger.debug("墨水屏已空闲")
    
    def _reset(self):
        """重置墨水屏"""
        if not HARDWARE_AVAILABLE or DEBUG_CONFIG['mock_hardware']:
            return
        
        GPIO.output(self.RST_PIN, 1)
        time.sleep(0.2)
        GPIO.output(self.RST_PIN, 0)
        time.sleep(0.002)
        GPIO.output(self.RST_PIN, 1)
        time.sleep(0.2)
    
    def _send_command(self, command):
        """发送命令"""
        if not HARDWARE_AVAILABLE or DEBUG_CONFIG['mock_hardware']:
            return
        
        GPIO.output(self.DC_PIN, 0)
        GPIO.output(self.CS_PIN, 0)
        self.spi.writebytes([command])
        GPIO.output(self.CS_PIN, 1)
    
    def _send_data(self, data):
        """发送数据"""
        if not HARDWARE_AVAILABLE or DEBUG_CONFIG['mock_hardware']:
            return
        
        GPIO.output(self.DC_PIN, 1)
        GPIO.output(self.CS_PIN, 0)
        self.spi.writebytes([data])
        GPIO.output(self.CS_PIN, 1)
    
    def _init_display(self):
        """初始化显示"""
        if not HARDWARE_AVAILABLE or DEBUG_CONFIG['mock_hardware']:
            return
        
        self._reset()
        self._wait_until_idle()
        
        # 发送初始化命令序列（根据具体墨水屏型号调整）
        if self.model == 'epd2in13_V4':
            self._init_epd2in13_v4()
        elif self.model == 'epd2in9_V2':
            self._init_epd2in9_v2()
        else:
            logger.warning(f"未知的墨水屏型号: {self.model}，使用默认初始化")
            self._init_default()
    
    def _init_epd2in13_v4(self):
        """初始化2.13英寸V4墨水屏"""
        # 这里是2.13英寸V4的具体初始化序列
        # 实际使用时需要根据厂商提供的驱动代码调整
        self._send_command(0x12)  # SWRESET
        self._wait_until_idle()
        
        self._send_command(0x01)  # Driver output control
        self._send_data(0xF9)
        self._send_data(0x00)
        self._send_data(0x00)
        
        self._send_command(0x11)  # Data entry mode
        self._send_data(0x01)
        
        logger.debug("2.13英寸V4墨水屏初始化完成")
    
    def _init_epd2in9_v2(self):
        """初始化2.9英寸V2墨水屏"""
        # 2.9英寸V2的初始化序列
        self._send_command(0x12)  # SWRESET
        self._wait_until_idle()
        
        logger.debug("2.9英寸V2墨水屏初始化完成")
    
    def _init_default(self):
        """默认初始化"""
        self._send_command(0x12)  # SWRESET
        self._wait_until_idle()
        
        logger.debug("默认墨水屏初始化完成")
    
    def create_content_image(self, content: Dict) -> Image.Image:
        """创建内容图像"""
        # 创建白色背景图像
        image = Image.new('1', (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)
        
        # 获取布局配置
        margins = LAYOUT_CONFIG['margins']
        sections = LAYOUT_CONFIG['sections']
        
        # 计算可用区域
        content_width = self.width - margins['left'] - margins['right']
        current_y = margins['top']
        
        try:
            # 绘制标题
            current_y = self._draw_header(draw, current_y, content_width, margins['left'])
            
            # 绘制单词部分
            if content.get('word'):
                current_y = self._draw_word_section(
                    draw, content['word'], current_y, content_width, margins['left']
                )
            
            # 绘制句子部分
            if content.get('quote'):
                current_y = self._draw_quote_section(
                    draw, content['quote'], current_y, content_width, margins['left']
                )
            
            # 绘制底部信息
            self._draw_footer(draw, content, margins['left'], margins['right'])
            
        except Exception as e:
            logger.error(f"创建内容图像失败: {e}")
            # 创建错误信息图像
            draw.text((10, 10), "Error creating content", font=self.fonts['definition'], fill=0)
        
        return image
    
    def _draw_header(self, draw: ImageDraw.Draw, y: int, width: int, x_offset: int) -> int:
        """绘制标题"""
        title = "Daily Word & Quote"
        font = self.fonts['title']
        
        # 计算文本尺寸
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 居中绘制
        x = x_offset + (width - text_width) // 2
        draw.text((x, y), title, font=font, fill=0)
        
        # 绘制分隔线
        if LAYOUT_CONFIG['separators']['show_lines']:
            line_y = y + text_height + 5
            draw.line([(x_offset, line_y), (x_offset + width, line_y)], fill=0, width=1)
            return line_y + 8
        
        return y + text_height + 8
    
    def _draw_word_section(self, draw: ImageDraw.Draw, word_data: Dict, y: int, width: int, x_offset: int) -> int:
        """绘制单词部分"""
        current_y = y
        
        # 绘制单词
        word = word_data.get('word', '').upper()
        word_font = self.fonts['word']
        draw.text((x_offset, current_y), word, font=word_font, fill=0)
        
        # 计算单词高度
        bbox = draw.textbbox((0, 0), word, font=word_font)
        word_height = bbox[3] - bbox[1]
        current_y += word_height + 2
        
        # 绘制音标
        phonetic = word_data.get('phonetic', '')
        if phonetic:
            phonetic_font = self.fonts['phonetic']
            draw.text((x_offset, current_y), phonetic, font=phonetic_font, fill=0)
            
            bbox = draw.textbbox((0, 0), phonetic, font=phonetic_font)
            phonetic_height = bbox[3] - bbox[1]
            current_y += phonetic_height + 4
        
        # 绘制定义
        definition = word_data.get('definition', '')
        if definition:
            current_y = self._draw_wrapped_text(
                draw, definition, x_offset, current_y, width, 
                self.fonts['definition'], max_lines=3
            )
        
        # 绘制例句
        example = word_data.get('example', '')
        if example:
            current_y += 4
            current_y = self._draw_wrapped_text(
                draw, f"Example: {example}", x_offset, current_y, width,
                self.fonts['example'], max_lines=2
            )
        
        return current_y + 8
    
    def _draw_quote_section(self, draw: ImageDraw.Draw, quote_data: Dict, y: int, width: int, x_offset: int) -> int:
        """绘制句子部分"""
        current_y = y
        
        # 绘制分隔线
        if LAYOUT_CONFIG['separators']['show_lines']:
            draw.line([(x_offset, current_y), (x_offset + width, current_y)], fill=0, width=1)
            current_y += 6
        
        # 绘制句子
        quote_text = quote_data.get('text', '')
        if quote_text:
            # 添加引号
            quote_text = f'"{quote_text}"'
            current_y = self._draw_wrapped_text(
                draw, quote_text, x_offset, current_y, width,
                self.fonts['quote'], max_lines=3
            )
        
        # 绘制作者
        author = quote_data.get('author', '')
        if author:
            current_y += 4
            author_text = f"— {author}"
            author_font = self.fonts['author']
            
            # 右对齐作者名
            bbox = draw.textbbox((0, 0), author_text, font=author_font)
            text_width = bbox[2] - bbox[0]
            x = x_offset + width - text_width
            
            draw.text((x, current_y), author_text, font=author_font, fill=0)
            
            author_height = bbox[3] - bbox[1]
            current_y += author_height
        
        return current_y + 8
    
    def _draw_footer(self, draw: ImageDraw.Draw, content: Dict, left_margin: int, right_margin: int):
        """绘制底部信息"""
        from daily_word_config import MONITOR_CONFIG
        from word_config_rpi import get_system_info
        
        footer_y = self.height - 20
        
        # 绘制日期
        date_str = datetime.now().strftime('%Y-%m-%d')
        date_font = self.fonts['date']
        draw.text((left_margin, footer_y), date_str, font=date_font, fill=0)
        
        # 绘制IP地址（如果启用）
        if MONITOR_CONFIG['monitored_metrics'].get('show_ip_address', False):
            try:
                sys_info = get_system_info()
                ip_address = sys_info.get('ip_address')
                if ip_address:
                    ip_text = f"IP: {ip_address}"
                    
                    # 计算IP文本位置（居中）
                    bbox = draw.textbbox((0, 0), ip_text, font=date_font)
                    ip_width = bbox[2] - bbox[0]
                    center_x = (self.width - ip_width) // 2
                    draw.text((center_x, footer_y), ip_text, font=date_font, fill=0)
            except Exception as e:
                logger.warning(f"获取IP地址失败: {e}")
        
        # 绘制来源信息（右对齐）
        sources = []
        if content.get('word', {}).get('source'):
            sources.append(f"W: {content['word']['source']}")
        if content.get('quote', {}).get('source'):
            sources.append(f"Q: {content['quote']['source']}")
        
        if sources:
            source_text = " | ".join(sources)
            bbox = draw.textbbox((0, 0), source_text, font=date_font)
            text_width = bbox[2] - bbox[0]
            x = self.width - right_margin - text_width
            draw.text((x, footer_y), source_text, font=date_font, fill=0)
    
    def _draw_wrapped_text(self, draw: ImageDraw.Draw, text: str, x: int, y: int, 
                          max_width: int, font: ImageFont.ImageFont, max_lines: int = None) -> int:
        """绘制自动换行文本"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # 单词太长，强制换行
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # 限制行数
        if max_lines and len(lines) > max_lines:
            lines = lines[:max_lines]
            if len(lines) == max_lines:
                lines[-1] = lines[-1][:50] + "..."
        
        # 绘制文本行
        current_y = y
        line_spacing = FONT_CONFIG['line_spacing']
        
        for line in lines:
            draw.text((x, current_y), line, font=font, fill=0)
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            current_y += line_height + line_spacing
        
        return current_y
    
    def display_content(self, content: Dict):
        """显示内容到墨水屏"""
        logger.info("开始显示内容到墨水屏...")
        
        try:
            # 创建内容图像
            image = self.create_content_image(content)
            
            # 保存预览图像（调试用）
            if DEBUG_CONFIG['debug_mode']:
                preview_path = Path("debug_preview.png")
                image.save(preview_path)
                logger.debug(f"预览图像已保存: {preview_path}")
            
            # 显示到墨水屏
            if HARDWARE_AVAILABLE and not DEBUG_CONFIG['mock_hardware']:
                self._display_image(image)
            else:
                logger.info("模拟模式：内容已准备好显示")
            
            logger.info("内容显示完成")
            
        except Exception as e:
            logger.error(f"显示内容失败: {e}")
            raise
    
    def _display_image(self, image: Image.Image):
        """将图像显示到墨水屏"""
        # 初始化显示
        self._init_display()
        
        # 转换图像数据
        image_data = self._convert_image_data(image)
        
        # 发送图像数据到墨水屏
        self._send_image_data(image_data)
        
        # 刷新显示
        self._refresh_display()
        
        logger.debug("图像已发送到墨水屏")
    
    def _convert_image_data(self, image: Image.Image) -> bytes:
        """转换图像数据格式"""
        # 确保图像是1位模式
        if image.mode != '1':
            image = image.convert('1')
        
        # 根据墨水屏要求转换数据格式
        image_data = []
        pixels = list(image.getdata())
        
        # 按字节打包像素数据
        for i in range(0, len(pixels), 8):
            byte_data = 0
            for j in range(8):
                if i + j < len(pixels):
                    if pixels[i + j] == 0:  # 黑色像素
                        byte_data |= (1 << (7 - j))
            image_data.append(byte_data)
        
        return bytes(image_data)
    
    def _send_image_data(self, image_data: bytes):
        """发送图像数据"""
        # 设置显示窗口
        self._set_memory_area(0, 0, self.width - 1, self.height - 1)
        self._set_memory_pointer(0, 0)
        
        # 发送图像数据
        self._send_command(0x24)  # WRITE_RAM
        for byte in image_data:
            self._send_data(byte)
    
    def _set_memory_area(self, x_start: int, y_start: int, x_end: int, y_end: int):
        """设置内存区域"""
        self._send_command(0x44)  # SET_RAM_X_ADDRESS_START_END_POSITION
        self._send_data((x_start >> 3) & 0xFF)
        self._send_data((x_end >> 3) & 0xFF)
        
        self._send_command(0x45)  # SET_RAM_Y_ADDRESS_START_END_POSITION
        self._send_data(y_start & 0xFF)
        self._send_data((y_start >> 8) & 0xFF)
        self._send_data(y_end & 0xFF)
        self._send_data((y_end >> 8) & 0xFF)
    
    def _set_memory_pointer(self, x: int, y: int):
        """设置内存指针"""
        self._send_command(0x4E)  # SET_RAM_X_ADDRESS_COUNTER
        self._send_data((x >> 3) & 0xFF)
        
        self._send_command(0x4F)  # SET_RAM_Y_ADDRESS_COUNTER
        self._send_data(y & 0xFF)
        self._send_data((y >> 8) & 0xFF)
    
    def _refresh_display(self):
        """刷新显示"""
        self._send_command(0x22)  # DISPLAY_UPDATE_CONTROL_2
        self._send_data(0xC4)
        self._send_command(0x20)  # MASTER_ACTIVATION
        self._wait_until_idle()
    
    def clear_display(self):
        """清空显示"""
        logger.info("清空墨水屏显示...")
        
        if not HARDWARE_AVAILABLE or DEBUG_CONFIG['mock_hardware']:
            logger.info("模拟模式：显示已清空")
            return
        
        try:
            self._init_display()
            
            # 创建白色图像
            white_image = Image.new('1', (self.width, self.height), 255)
            image_data = self._convert_image_data(white_image)
            
            # 发送白色数据
            self._send_image_data(image_data)
            self._refresh_display()
            
            logger.info("墨水屏已清空")
            
        except Exception as e:
            logger.error(f"清空显示失败: {e}")
            raise
    
    def sleep(self):
        """进入睡眠模式"""
        if not HARDWARE_AVAILABLE or DEBUG_CONFIG['mock_hardware']:
            return
        
        self._send_command(0x10)  # DEEP_SLEEP_MODE
        self._send_data(0x01)
        logger.info("墨水屏已进入睡眠模式")
    
    def cleanup(self):
        """清理资源"""
        if HARDWARE_AVAILABLE and not DEBUG_CONFIG['mock_hardware']:
            try:
                self.sleep()
                if hasattr(self, 'spi'):
                    self.spi.close()
                GPIO.cleanup()
                logger.info("硬件资源已清理")
            except Exception as e:
                logger.error(f"清理硬件资源失败: {e}")

def main():
    """测试函数"""
    import sys
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建显示控制器
    controller = DailyWordDisplayController()
    
    # 测试内容
    test_content = {
        'word': {
            'word': 'serendipity',
            'phonetic': '/ˌserənˈdipədē/',
            'definition': 'The occurrence and development of events by chance in a happy or beneficial way.',
            'example': 'A fortunate stroke of serendipity brought the two old friends together.',
            'source': 'Test API'
        },
        'quote': {
            'text': 'The only way to do great work is to love what you do.',
            'author': 'Steve Jobs',
            'category': 'motivation',
            'source': 'Test API'
        },
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == '--clear':
                controller.clear_display()
            elif sys.argv[1] == '--test':
                controller.display_content(test_content)
            else:
                print("用法: python daily_word_display_controller.py [--clear|--test]")
        else:
            controller.display_content(test_content)
    
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        logger.error(f"测试失败: {e}")
    finally:
        controller.cleanup()

if __name__ == "__main__":
    main()