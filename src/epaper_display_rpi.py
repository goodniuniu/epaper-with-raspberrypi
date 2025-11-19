#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
树莓派墨水屏显示模块
支持多种墨水屏型号
"""

import logging
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys

# 添加配置
sys.path.append(str(Path(__file__).parent))
from word_config_rpi import DISPLAY_CONFIG, SYSTEM_CONFIG

class EPaperDisplay:
    """墨水屏显示控制器"""
    
    def __init__(self, epd_type=None):
        """
        初始化墨水屏显示器
        
        参数:
        - epd_type: 墨水屏类型 ('waveshare_2in7', 'waveshare_4in2', 'luma_epd')
        """
        self.epd_type = epd_type or DISPLAY_CONFIG['epd_type']
        self.width = DISPLAY_CONFIG['width']
        self.height = DISPLAY_CONFIG['height']
        self.epd = None
        
        # 加载字体
        self.fonts = self._load_fonts()
        
        # 初始化墨水屏
        self._init_epd()
    
    def _load_fonts(self):
        """加载字体文件"""
        fonts = {}
        font_config = DISPLAY_CONFIG['fonts']
        font_sizes = DISPLAY_CONFIG['font_sizes']
        
        try:
            for name, size in font_sizes.items():
                font_path = font_config.get('default')
                if name in ['title', 'word'] and 'bold' in font_config:
                    font_path = font_config['bold']
                
                fonts[name] = ImageFont.truetype(font_path, size)
                
        except Exception as e:
            logging.warning(f"字体加载失败，使用默认字体: {e}")
            # 使用默认字体
            for name, size in font_sizes.items():
                fonts[name] = ImageFont.load_default()
        
        return fonts
    
    def _init_epd(self):
        """初始化墨水屏"""
        try:
            if self.epd_type == 'waveshare_2in7':
                self._init_waveshare_2in7()
            elif self.epd_type == 'waveshare_4in2':
                self._init_waveshare_4in2()
            elif self.epd_type == 'luma_epd':
                self._init_luma_epd()
            else:
                logging.warning(f"未知的墨水屏类型: {self.epd_type}")
                self.epd = None
                
        except Exception as e:
            logging.error(f"墨水屏初始化失败: {e}")
            self.epd = None
    
    def _init_waveshare_2in7(self):
        """初始化Waveshare 2.7寸墨水屏"""
        try:
            import epd2in7
            self.epd = epd2in7.EPD()
            self.epd.init()
            self.epd.Clear(0xFF)
            logging.info("Waveshare 2.7寸墨水屏初始化成功")
        except ImportError:
            logging.error("未找到epd2in7模块，请安装waveshare-epd库")
            raise
    
    def _init_waveshare_4in2(self):
        """初始化Waveshare 4.2寸墨水屏"""
        try:
            import epd4in2
            self.epd = epd4in2.EPD()
            self.epd.init()
            self.epd.Clear(0xFF)
            logging.info("Waveshare 4.2寸墨水屏初始化成功")
        except ImportError:
            logging.error("未找到epd4in2模块，请安装waveshare-epd库")
            raise
    
    def _init_luma_epd(self):
        """初始化Luma EPD墨水屏"""
        try:
            from luma.core.interface.serial import spi
            from luma.core.render import canvas
            from luma.epd.device import ssd1675
            
            serial = spi(device=0, port=0)
            self.epd = ssd1675(serial)
            logging.info("Luma EPD墨水屏初始化成功")
        except ImportError:
            logging.error("未找到luma.epd模块，请安装luma.epd库")
            raise
    
    def display_content(self, word_data, sentence_data):
        """
        在墨水屏上显示内容
        
        参数:
        - word_data: 单词数据字典
        - sentence_data: 句子数据字典
        """
        if not self.epd:
            logging.warning("墨水屏未初始化，无法显示内容")
            return False
        
        try:
            # 创建图像
            image = Image.new('1', (self.width, self.height), 255)
            draw = ImageDraw.Draw(image)
            
            # 绘制内容
            self._draw_content(draw, word_data, sentence_data)
            
            # 显示到墨水屏
            if self.epd_type.startswith('waveshare'):
                self.epd.display(self.epd.getbuffer(image))
            elif self.epd_type == 'luma_epd':
                self.epd.display(image)
            
            logging.info("内容已显示到墨水屏")
            return True
            
        except Exception as e:
            logging.error(f"显示内容时出错: {e}")
            return False
    
    def _draw_content(self, draw, word_data, sentence_data):
        """绘制内容到图像"""
        margins = DISPLAY_CONFIG['margins']
        spacing = DISPLAY_CONFIG['spacing']
        
        x = margins['left']
        y = margins['top']
        
        # 绘制标题
        title = "Daily Word & Quote"
        draw.text((x, y), title, font=self.fonts['title'], fill=0)
        y += self.fonts['title'].getsize(title)[1] + spacing['section']
        
        # 绘制分隔线
        draw.line([(x, y), (self.width - margins['right'], y)], fill=0, width=1)
        y += spacing['paragraph']
        
        # 绘制单词部分
        if word_data and word_data.get('word'):
            y = self._draw_word_section(draw, word_data, x, y)
            y += spacing['section']
        
        # 绘制分隔线
        if y < self.height - 50:  # 确保有足够空间
            draw.line([(x, y), (self.width - margins['right'], y)], fill=0, width=1)
            y += spacing['paragraph']
            
            # 绘制句子部分
            if sentence_data and sentence_data.get('sentence'):
                y = self._draw_sentence_section(draw, sentence_data, x, y)
        
        # 绘制日期
        import datetime
        date_str = datetime.date.today().strftime('%Y-%m-%d')
        date_width = self.fonts['date'].getsize(date_str)[0]
        draw.text((self.width - margins['right'] - date_width, 
                  self.height - margins['bottom'] - self.fonts['date'].getsize(date_str)[1]), 
                 date_str, font=self.fonts['date'], fill=0)
    
    def _draw_word_section(self, draw, word_data, x, y):
        """绘制单词部分"""
        spacing = DISPLAY_CONFIG['spacing']
        max_width = self.width - DISPLAY_CONFIG['margins']['left'] - DISPLAY_CONFIG['margins']['right']
        
        # 单词标题
        word_title = f"📚 {word_data['word'].upper()}"
        draw.text((x, y), word_title, font=self.fonts['word'], fill=0)
        y += self.fonts['word'].getsize(word_title)[1] + spacing['line']
        
        # 发音
        if word_data.get('pronunciation'):
            draw.text((x + 10, y), word_data['pronunciation'], font=self.fonts['definition'], fill=0)
            y += self.fonts['definition'].getsize(word_data['pronunciation'])[1] + spacing['paragraph']
        
        # 定义
        if word_data.get('definition'):
            def_lines = self._wrap_text(word_data['definition'], self.fonts['definition'], max_width - 20)
            for line in def_lines:
                draw.text((x + 10, y), line, font=self.fonts['definition'], fill=0)
                y += self.fonts['definition'].getsize(line)[1] + spacing['line']
            y += spacing['paragraph']
        
        # 例句
        if word_data.get('example'):
            example_lines = self._wrap_text(f"Example: {word_data['example']}", 
                                          self.fonts['example'], max_width - 20)
            for line in example_lines:
                draw.text((x + 10, y), line, font=self.fonts['example'], fill=0)
                y += self.fonts['example'].getsize(line)[1] + spacing['line']
        
        return y
    
    def _draw_sentence_section(self, draw, sentence_data, x, y):
        """绘制句子部分"""
        spacing = DISPLAY_CONFIG['spacing']
        max_width = self.width - DISPLAY_CONFIG['margins']['left'] - DISPLAY_CONFIG['margins']['right']
        
        # 句子标题
        quote_title = "💭 Quote of the Day:"
        draw.text((x, y), quote_title, font=self.fonts['quote'], fill=0)
        y += self.fonts['quote'].getsize(quote_title)[1] + spacing['paragraph']
        
        # 句子内容
        if sentence_data.get('sentence'):
            sentence_text = f'"{sentence_data["sentence"]}"'
            sentence_lines = self._wrap_text(sentence_text, self.fonts['quote'], max_width - 20)
            for line in sentence_lines:
                draw.text((x + 10, y), line, font=self.fonts['quote'], fill=0)
                y += self.fonts['quote'].getsize(line)[1] + spacing['line']
            y += spacing['paragraph']
        
        # 作者
        if sentence_data.get('author'):
            author_text = f"— {sentence_data['author']}"
            draw.text((x + 20, y), author_text, font=self.fonts['author'], fill=0)
            y += self.fonts['author'].getsize(author_text)[1]
        
        return y
    
    def _wrap_text(self, text, font, max_width):
        """文本自动换行"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.getsize(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def clear_display(self):
        """清空显示"""
        if self.epd:
            try:
                if self.epd_type.startswith('waveshare'):
                    self.epd.Clear(0xFF)
                elif self.epd_type == 'luma_epd':
                    with canvas(self.epd) as draw:
                        draw.rectangle(self.epd.bounding_box, outline="white", fill="white")
                logging.info("墨水屏已清空")
            except Exception as e:
                logging.error(f"清空墨水屏时出错: {e}")
    
    def sleep(self):
        """墨水屏进入睡眠模式"""
        if self.epd:
            try:
                if hasattr(self.epd, 'sleep'):
                    self.epd.sleep()
                logging.info("墨水屏进入睡眠模式")
            except Exception as e:
                logging.error(f"墨水屏睡眠时出错: {e}")
    
    def __del__(self):
        """析构函数"""
        self.sleep()