#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - 优化的显示控制器
Daily Word E-Paper Display System - Optimized Display Controller

集成缓存、对象池和性能监控的优化版本
"""

import logging
import time
import threading
import json
from typing import Dict, Optional, Any
from pathlib import Path
from datetime import datetime

# 导入优化组件
from cache_manager import get_cache_manager, cache_result
from image_pool import get_image_pool, get_font_cache, OptimizedDisplayContext
from performance_monitor import display_performance, get_performance_metrics
from daily_word_config import (
    EPAPER_CONFIG, FONT_CONFIG, LAYOUT_CONFIG, THEME_CONFIG,
    DEBUG_CONFIG, DATA_DIR
)

# 导入基础显示组件
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("警告: PIL库未安装，请运行: pip install Pillow")
    exit(1)

# 尝试导入墨水屏驱动
try:
    import spidev
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    print("警告: 硬件库未安装，运行在模拟模式")
    HARDWARE_AVAILABLE = False

logger = logging.getLogger(__name__)


class OptimizedDailyWordDisplayController:
    """优化的每日单词显示控制器"""
    
    def __init__(self):
        """初始化优化的显示控制器"""
        self.width = EPAPER_CONFIG['width']
        self.height = EPAPER_CONFIG['height']
        self.model = EPAPER_CONFIG['model']
        
        # 获取当前主题
        self.current_theme = THEME_CONFIG['themes'][THEME_CONFIG['current_theme']]
        
        # 初始化缓存管理器
        self.cache_manager = get_cache_manager()
        
        # 初始化图像对象池
        self.image_pool = get_image_pool(self.width, self.height)
        
        # 初始化字体缓存
        self.font_cache = get_font_cache()
        
        # 初始化字体配置
        self.fonts = self._initialize_fonts()
        
        # 初始化硬件
        if HARDWARE_AVAILABLE and not DEBUG_CONFIG['mock_hardware']:
            self._init_hardware()
        else:
            logger.warning("运行在模拟模式，不会实际控制硬件")
        
        # 性能指标
        self._stats = {
            'images_created': 0,
            'images_reused': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'display_updates': 0
        }
        
        logger.info(f"优化显示控制器初始化完成 - 型号: {self.model}, 尺寸: {self.width}x{self.height}")
    
    def _initialize_fonts(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """初始化字体（使用缓存）"""
        fonts = {}
        font_paths = FONT_CONFIG['font_paths']
        font_sizes = FONT_CONFIG['font_sizes']
        
        for font_type, size in font_sizes.items():
            # 确定字体路径
            if font_type in ['title', 'word'] and 'bold' in font_paths:
                font_path = font_paths['bold']
            elif font_type in ['phonetic', 'example'] and 'mono' in font_paths:
                font_path = font_paths['mono']
            else:
                font_path = font_paths.get('default', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
            
            # 从缓存获取字体
            font = self.font_cache.get_font(font_path, size)
            if font:
                fonts[font_type] = font
                logger.debug(f"字体已缓存: {font_type} - {font_path} ({size}px)")
            else:
                # 回退到默认字体
                fonts[font_type] = ImageFont.load_default()
                logger.warning(f"字体缓存失败，使用默认字体: {font_type}")
        
        return fonts
    
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
    
    @display_performance
    def create_content_image(self, content: Dict) -> Optional[Image.Image]:
        """创建内容图像（优化版本）"""
        try:
            # 生成缓存key
            cache_key = self._generate_content_cache_key(content)
            
            # 尝试从缓存获取图像
            cached_image = self.cache_manager.get(cache_key, max_age=1800)  # 30分钟缓存
            if cached_image and isinstance(cached_image, bytes):
                # 从缓存获取的图像数据
                import io
                image = Image.open(io.BytesIO(cached_image))
                self._stats['cache_hits'] += 1
                logger.debug(f"内容图像缓存命中: {cache_key}")
                return image
            
            self._stats['cache_misses'] += 1
            
            # 从对象池获取图像
            image = self.image_pool.get_image()
            if not image:
                logger.error("无法从对象池获取图像")
                return None
            
            self._stats['images_reused'] += 1
            
            # 创建绘图上下文
            draw = ImageDraw.Draw(image)
            
            # 获取布局配置
            margins = LAYOUT_CONFIG['margins']
            current_y = margins['top']
            
            # 绘制内容
            current_y = self._draw_header(draw, current_y, margins['left'])
            current_y = self._draw_word_section(draw, content.get('word', {}), current_y, margins['left'])
            current_y = self._draw_quote_section(draw, content.get('quote', {}), current_y, margins['left'])
            self._draw_footer(draw, content, margins['left'], margins['right'])
            
            # 缓存图像
            if DEBUG_CONFIG['debug_mode']:
                self._cache_image(image, cache_key)
            
            return image
            
        except Exception as e:
            logger.error(f"创建内容图像失败: {e}")
            # 确保返回对象到池中
            if 'image' in locals() and image:
                self.image_pool.return_image(image)
            return None
    
    def _generate_content_cache_key(self, content: Dict) -> str:
        """生成内容缓存key"""
        # 基于内容生成唯一的缓存key
        content_str = json.dumps(content, sort_keys=True)
        date_str = datetime.now().strftime('%Y-%m-%d')
        return f"content_image:{date_str}:{hash(content_str) % 10000}"
    
    def _cache_image(self, image: Image.Image, cache_key: str):
        """缓存图像"""
        try:
            import io
            image_buffer = io.BytesIO()
            image.save(image_buffer, format='PNG')
            image_data = image_buffer.getvalue()
            
            self.cache_manager.set(cache_key, image_data, ttl=1800)
            logger.debug(f"图像已缓存: {cache_key}")
        except Exception as e:
            logger.warning(f"缓存图像失败: {e}")
    
    def _draw_header(self, draw: ImageDraw.Draw, y: int, x_offset: int) -> int:
        """绘制标题（使用缓存字体）"""
        title = "Daily Word & Quote"
        font = self.fonts.get('title')
        
        if font:
            # 计算文本尺寸
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 居中绘制
            x = x_offset + (self.width - x_offset * 2 - text_width) // 2
            draw.text((x, y), title, font=font, fill=0)
            
            # 绘制分隔线
            if LAYOUT_CONFIG['separators']['show_lines']:
                line_y = y + text_height + 5
                draw.line([(x_offset, line_y), (self.width - x_offset, line_y)], fill=0, width=1)
                return line_y + 8
            
            return y + text_height + 8
        
        return y + 20
    
    def _draw_word_section(self, draw: ImageDraw.Draw, word_data: Dict, y: int, x_offset: int) -> int:
        """绘制单词部分"""
        if not word_data:
            return y
        
        current_y = y
        
        # 绘制单词
        word = word_data.get('word', '').upper()
        word_font = self.fonts.get('word')
        if word_font:
            draw.text((x_offset, current_y), word, font=word_font, fill=0)
            
            # 计算单词高度
            bbox = draw.textbbox((0, 0), word, font=word_font)
            word_height = bbox[3] - bbox[1]
            current_y += word_height + 2
        
        # 绘制音标
        phonetic = word_data.get('phonetic', '')
        if phonetic:
            phonetic_font = self.fonts.get('phonetic')
            if phonetic_font:
                draw.text((x_offset, current_y), phonetic, font=phonetic_font, fill=0)
                
                bbox = draw.textbbox((0, 0), phonetic, font=phonetic_font)
                phonetic_height = bbox[3] - bbox[1]
                current_y += phonetic_height + 4
        
        # 绘制定义
        definition = word_data.get('definition', '')
        if definition:
            current_y = self._draw_wrapped_text(
                draw, definition, x_offset, current_y, self.width - x_offset * 2,
                self.fonts.get('definition'), max_lines=3
            )
        
        # 绘制例句
        example = word_data.get('example', '')
        if example:
            current_y += 4
            current_y = self._draw_wrapped_text(
                draw, f"Example: {example}", x_offset, current_y, self.width - x_offset * 2,
                self.fonts.get('example'), max_lines=2
            )
        
        return current_y + 8
    
    def _draw_quote_section(self, draw: ImageDraw.Draw, quote_data: Dict, y: int, x_offset: int) -> int:
        """绘制句子部分"""
        if not quote_data:
            return y
        
        current_y = y
        
        # 绘制分隔线
        if LAYOUT_CONFIG['separators']['show_lines']:
            draw.line([(x_offset, current_y), (self.width - x_offset, current_y)], fill=0, width=1)
            current_y += 6
        
        # 绘制句子
        quote_text = quote_data.get('text', '')
        if quote_text:
            # 添加引号
            quote_text = f'"{quote_text}"'
            current_y = self._draw_wrapped_text(
                draw, quote_text, x_offset, current_y, self.width - x_offset * 2,
                self.fonts.get('quote'), max_lines=3
            )
        
        # 绘制作者
        author = quote_data.get('author', '')
        if author:
            current_y += 4
            author_text = f"— {author}"
            author_font = self.fonts.get('author')
            
            if author_font:
                # 右对齐作者名
                bbox = draw.textbbox((0, 0), author_text, font=author_font)
                text_width = bbox[2] - bbox[0]
                x = self.width - x_offset - text_width
                
                draw.text((x, current_y), author_text, font=author_font, fill=0)
                
                author_height = bbox[3] - bbox[1]
                current_y += author_height
        
        return current_y + 8
    
    def _draw_wrapped_text(self, draw: ImageDraw.Draw, text: str, x: int, y: int, 
                          max_width: int, font: Optional[ImageFont.FreeTypeFont], max_lines: int = None) -> int:
        """绘制自动换行文本（优化版本）"""
        if not font or not text:
            return y
        
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
    
    def _draw_footer(self, draw: ImageDraw.Draw, content: Dict, left_margin: int, right_margin: int):
        """绘制底部信息"""
        footer_y = self.height - 20
        
        # 绘制日期
        date_str = datetime.now().strftime('%Y-%m-%d')
        date_font = self.fonts.get('date')
        if date_font:
            draw.text((left_margin, footer_y), date_str, font=date_font, fill=0)
        
        # 绘制来源信息（右对齐）
        sources = []
        if content.get('word', {}).get('source'):
            sources.append(f"W: {content['word']['source']}")
        if content.get('quote', {}).get('source'):
            sources.append(f"Q: {content['quote']['source']}")
        
        if sources and date_font:
            source_text = " | ".join(sources)
            bbox = draw.textbbox((0, 0), source_text, font=date_font)
            text_width = bbox[2] - bbox[0]
            x = self.width - right_margin - text_width
            draw.text((x, footer_y), source_text, font=date_font, fill=0)
    
    @display_performance
    def display_content(self, content: Dict) -> bool:
        """显示内容到墨水屏（优化版本）"""
        logger.info("开始优化显示内容...")
        
        try:
            # 创建内容图像
            image = self.create_content_image(content)
            if not image:
                logger.error("创建内容图像失败")
                return False
            
            # 保存预览图像（调试用）
            if DEBUG_CONFIG['debug_mode']:
                self._save_preview_image(image)
            
            # 显示到墨水屏
            if HARDWARE_AVAILABLE and not DEBUG_CONFIG['mock_hardware']:
                success = self._display_image(image)
                # 确保返回图像到对象池
                self.image_pool.return_image(image)
                return success
            else:
                logger.info("模拟模式：内容已准备好显示")
                # 模拟模式下也返回对象到池
                self.image_pool.return_image(image)
                return True
                
        except Exception as e:
            logger.error(f"显示内容失败: {e}")
            return False
    
    def _save_preview_image(self, image: Image.Image):
        """保存预览图像"""
        try:
            preview_dir = Path(DATA_DIR) / "previews"
            preview_dir.mkdir(parents=True, exist_ok=True)
            
            preview_path = preview_dir / f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image.save(preview_path)
            logger.debug(f"预览图像已保存: {preview_path}")
        except Exception as e:
            logger.warning(f"保存预览图像失败: {e}")
    
    def _display_image(self, image: Image.Image) -> bool:
        """将图像显示到墨水屏"""
        try:
            # 初始化显示
            self._init_display()
            
            # 转换图像数据
            image_data = self._convert_image_data(image)
            
            # 发送图像数据到墨水屏
            self._send_image_data(image_data)
            
            # 刷新显示
            self._refresh_display()
            
            self._stats['display_updates'] += 1
            logger.debug("图像已发送到墨水屏")
            return True
            
        except Exception as e:
            logger.error(f"显示图像失败: {e}")
            return False
    
    def _convert_image_data(self, image: Image.Image) -> bytes:
        """转换图像数据格式"""
        if image.mode != '1':
            image = image.convert('1')
        
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
    
    def _wait_until_idle(self):
        """等待墨水屏空闲"""
        if not HARDWARE_AVAILABLE or DEBUG_CONFIG['mock_hardware']:
            return
        
        while GPIO.input(self.BUSY_PIN) == 1:
            time.sleep(0.01)
    
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
        
        # 根据型号发送初始化命令
        if self.model == 'epd2in13_V4':
            self._init_epd2in13_v4()
        elif self.model == 'epd2in9_V2':
            self._init_epd2in9_v2()
        else:
            logger.warning(f"未知的墨水屏型号: {self.model}，使用默认初始化")
            self._init_default()
    
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
    
    def _init_epd2in13_v4(self):
        """初始化2.13英寸V4墨水屏"""
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
        self._send_command(0x12)  # SWRESET
        self._wait_until_idle()
        
        logger.debug("2.9英寸V2墨水屏初始化完成")
    
    def _init_default(self):
        """默认初始化"""
        self._send_command(0x12)  # SWRESET
        self._wait_until_idle()
        
        logger.debug("默认墨水屏初始化完成")
    
    def clear_display(self) -> bool:
        """清空显示"""
        logger.info("清空墨水屏显示...")
        
        if not HARDWARE_AVAILABLE or DEBUG_CONFIG['mock_hardware']:
            logger.info("模拟模式：显示已清空")
            return True
        
        try:
            self._init_display()
            
            # 从对象池获取白色图像
            white_image = self.image_pool.get_image()
            if white_image:
                image_data = self._convert_image_data(white_image)
                
                # 发送白色数据
                self._send_image_data(image_data)
                self._refresh_display()
                
                # 返回对象到池
                self.image_pool.return_image(white_image)
                
                logger.info("墨水屏已清空")
                return True
            else:
                logger.error("无法获取白色图像对象")
                return False
                
        except Exception as e:
            logger.error(f"清空显示失败: {e}")
            return False
    
    def sleep(self):
        """进入睡眠模式"""
        if not HARDWARE_AVAILABLE or DEBUG_CONFIG['mock_hardware']:
            return
        
        self._send_command(0x10)  # DEEP_SLEEP_MODE
        self._send_data(0x01)
        logger.info("墨水屏已进入睡眠模式")
    
    def cleanup(self):
        """清理资源"""
        logger.info("清理优化显示控制器资源...")
        
        # 清理对象池
        self.image_pool.cleanup()
        
        if HARDWARE_AVAILABLE and not DEBUG_CONFIG['mock_hardware']:
            try:
                self.sleep()
                if hasattr(self, 'spi'):
                    self.spi.close()
                GPIO.cleanup()
                logger.info("硬件资源已清理")
            except Exception as e:
                logger.error(f"清理硬件资源失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取优化统计"""
        return {
            'cache': self.cache_manager.get_stats() if hasattr(self.cache_manager, 'get_stats') else {},
            'image_pool': self.image_pool.get_stats(),
            'font_cache': self.font_cache.get_stats(),
            'controller': self._stats.copy()
        }


# 向后兼容的接口
class DailyWordDisplayController(OptimizedDailyWordDisplayController):
    """向后兼容的显示控制器"""
    pass


def main():
    """测试函数"""
    import sys
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("优化显示控制器测试开始...")
    
    # 创建优化显示控制器
    controller = OptimizedDailyWordDisplayController()
    
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
            elif sys.argv[1] == '--stats':
                stats = controller.get_stats()
                print("\n优化统计:")
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            else:
                print("用法: python optimized_display_controller.py [--clear|--test|--stats]")
        else:
            controller.display_content(test_content)
            
            # 显示统计
            stats = controller.get_stats()
            print("\n性能统计:")
            print(f"缓存命中率: {stats['cache'].get('hit_rate', 0):.2%}")
            print(f"图像对象重用: {stats['controller']['images_reused']}")
            print(f"字体缓存数量: {stats['font_cache']['cached_fonts']}")
    
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        logger.error(f"测试失败: {e}")
    finally:
        controller.cleanup()
        print("\n✅ 优化显示控制器测试完成!")


if __name__ == "__main__":
    main()