#!/usr/bin/env python3
"""
每日单词墨水屏显示系统 - 基于示例代码的显示控制器
Daily Word E-Paper Display System - Display Controller based on example code
"""

import os
import sys
import time
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 导入我们创建的驱动模块
try:
    from waveshare_epd import epd3in52
    import text_wrap
    import get_ipaddress
    EPAPER_AVAILABLE = True
except ImportError as e:
    print(f"警告: 墨水屏驱动导入失败: {e}")
    EPAPER_AVAILABLE = False

# 配置日志
logger = logging.getLogger(__name__)

class DailyWordEPaperDisplay:
    """每日单词墨水屏显示器"""
    
    def __init__(self):
        """初始化显示器"""
        self.width = 360
        self.height = 240
        
        # 字体路径配置
        self.font_paths = self._get_font_paths()
        
        if EPAPER_AVAILABLE:
            try:
                self.epd = epd3in52.EPD()
                self.epd.init()
                logger.info(f"墨水屏初始化完成 - 尺寸: {self.width}x{self.height}")
            except Exception as e:
                logger.error(f"墨水屏初始化失败: {e}")
                self.epd = None
        else:
            self.epd = None
            logger.warning("运行在模拟模式")
    
    def _get_font_paths(self):
        """获取字体路径"""
        # 尝试多个可能的字体路径
        font_candidates = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/TTF/DejaVuSans.ttf',
            '/System/Library/Fonts/Arial.ttf',  # macOS
            'C:/Windows/Fonts/arial.ttf',  # Windows
        ]
        
        # 检查项目目录中的字体
        project_fonts = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pic', 'Font.ttc'),
            os.path.join(os.path.dirname(__file__), 'fonts', 'Font.ttc'),
        ]
        
        font_candidates = project_fonts + font_candidates
        
        for font_path in font_candidates:
            if os.path.exists(font_path):
                return font_path
        
        logger.warning("未找到合适的字体文件，将使用默认字体")
        return None
    
    def _load_fonts(self):
        """加载字体"""
        fonts = {}
        
        try:
            if self.font_paths:
                fonts['large'] = ImageFont.truetype(self.font_paths, 24)
                fonts['medium'] = ImageFont.truetype(self.font_paths, 18)
                fonts['small'] = ImageFont.truetype(self.font_paths, 12)
                fonts['title'] = ImageFont.truetype(self.font_paths, 20)
            else:
                # 使用默认字体
                fonts['large'] = ImageFont.load_default()
                fonts['medium'] = ImageFont.load_default()
                fonts['small'] = ImageFont.load_default()
                fonts['title'] = ImageFont.load_default()
        except Exception as e:
            logger.warning(f"字体加载失败: {e}，使用默认字体")
            fonts = {
                'large': ImageFont.load_default(),
                'medium': ImageFont.load_default(),
                'small': ImageFont.load_default(),
                'title': ImageFont.load_default()
            }
        
        return fonts
    
    def display_daily_content(self, content):
        """显示每日内容"""
        logger.info("开始显示每日内容到墨水屏...")
        
        try:
            # 创建图像
            image = Image.new('1', (self.width, self.height), 255)  # 白色背景
            draw = ImageDraw.Draw(image)
            fonts = self._load_fonts()
            
            # 绘制内容
            y_pos = 10
            
            # 标题
            title = "Daily Word & Quote"
            draw.text((10, y_pos), title, font=fonts['title'], fill=0)
            y_pos += 30
            
            # 绘制分隔线
            draw.line([(10, y_pos), (self.width - 10, y_pos)], fill=0, width=1)
            y_pos += 10
            
            # 每日单词
            if content.get('word'):
                word_data = content['word']
                
                # 单词
                word = word_data.get('word', '').upper()
                draw.text((10, y_pos), f"Word: {word}", font=fonts['large'], fill=0)
                y_pos += 30
                
                # 音标
                phonetic = word_data.get('phonetic', '')
                if phonetic:
                    draw.text((10, y_pos), phonetic, font=fonts['medium'], fill=0)
                    y_pos += 25
                
                # 定义
                definition = word_data.get('definition', '')
                if definition:
                    # 文本换行
                    wrapped_def = self._wrap_text(definition, fonts['medium'], self.width - 20)
                    for line in wrapped_def[:2]:  # 最多显示2行
                        draw.text((10, y_pos), line, font=fonts['medium'], fill=0)
                        y_pos += 20
            
            y_pos += 10
            
            # 每日句子
            if content.get('quote'):
                quote_data = content['quote']
                
                # 绘制分隔线
                draw.line([(10, y_pos), (self.width - 10, y_pos)], fill=0, width=1)
                y_pos += 10
                
                # 句子
                quote_text = quote_data.get('text', '')
                if quote_text:
                    quote_text = f'"{quote_text}"'
                    wrapped_quote = self._wrap_text(quote_text, fonts['medium'], self.width - 20)
                    for line in wrapped_quote[:3]:  # 最多显示3行
                        draw.text((10, y_pos), line, font=fonts['medium'], fill=0)
                        y_pos += 20
                
                # 作者
                author = quote_data.get('author', '')
                if author:
                    author_text = f"— {author}"
                    draw.text((self.width - 150, y_pos), author_text, font=fonts['small'], fill=0)
            
            # 底部信息
            self._draw_footer(draw, fonts)
            
            # 显示到墨水屏
            if self.epd:
                self.epd.Clear()
                self.epd.display(self.epd.getbuffer(image))
                self.epd.lut_GC()
                self.epd.refresh()
                time.sleep(2)
                logger.info("内容已显示到墨水屏")
            else:
                logger.info("模拟模式：内容已准备好显示")
                # 保存预览图像
                preview_path = "/opt/daily-word-epaper/debug_preview.png"
                image.save(preview_path)
                logger.info(f"预览图像已保存: {preview_path}")
            
        except Exception as e:
            logger.error(f"显示内容失败: {e}")
            raise
    
    def _wrap_text(self, text, font, max_width):
        """文本自动换行"""
        if not text:
            return []
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # 简化的宽度计算
            if len(test_line) * 8 <= max_width:  # 假设每个字符8像素宽
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _draw_footer(self, draw, fonts):
        """绘制底部信息"""
        footer_y = self.height - 25
        
        # 日期
        date_str = datetime.now().strftime('%Y-%m-%d')
        draw.text((10, footer_y), date_str, font=fonts['small'], fill=0)
        
        # IP地址
        try:
            ip_address = get_ipaddress.get_ip_address()
            if ip_address:
                ip_text = f"IP: {ip_address}"
                # 居中显示
                draw.text((120, footer_y), ip_text, font=fonts['small'], fill=0)
        except Exception as e:
            logger.warning(f"获取IP地址失败: {e}")
        
        # 版本信息
        draw.text((self.width - 80, footer_y), "v1.0.0", font=fonts['small'], fill=0)
    
    def clear_display(self):
        """清空显示"""
        logger.info("清空墨水屏显示...")
        
        if self.epd:
            try:
                self.epd.Clear()
                logger.info("墨水屏已清空")
            except Exception as e:
                logger.error(f"清空显示失败: {e}")
        else:
            logger.info("模拟模式：显示已清空")
    
    def sleep(self):
        """进入睡眠模式"""
        if self.epd:
            try:
                self.epd.sleep()
                logger.info("墨水屏已进入睡眠模式")
            except Exception as e:
                logger.error(f"进入睡眠模式失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self.sleep()
            if EPAPER_AVAILABLE:
                epd3in52.epdconfig.module_exit(cleanup=True)
            logger.info("显示器资源已清理")
        except Exception as e:
            logger.error(f"清理资源失败: {e}")

def main():
    """测试函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建显示器
    display = DailyWordEPaperDisplay()
    
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
        }
    }
    
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == '--clear':
                display.clear_display()
            elif sys.argv[1] == '--test':
                display.display_daily_content(test_content)
            else:
                print("用法: python daily_word_display_epaper.py [--clear|--test]")
        else:
            display.display_daily_content(test_content)
    
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        logger.error(f"测试失败: {e}")
    finally:
        display.cleanup()

if __name__ == "__main__":
    main()