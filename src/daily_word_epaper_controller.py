#!/usr/bin/env python3
"""
每日单词墨水屏显示控制器 - 基于用户工作代码
Daily Word E-Paper Display Controller - Based on Working User Code
"""

import os
import sys
import time
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 设置图片和字体路径
picdir = os.path.join(os.path.dirname(current_dir), 'pic')

try:
    from waveshare_epd import epd3in52
    import text_wrap
    import get_ipaddress
    EPD_AVAILABLE = True
except ImportError as e:
    logging.warning(f"墨水屏模块导入失败: {e}")
    EPD_AVAILABLE = False


class DailyWordEPaperController:
    """每日单词墨水屏显示控制器"""
    
    def __init__(self):
        """初始化墨水屏控制器"""
        self.logger = logging.getLogger(__name__)
        self.epd = None
        self.font_path = os.path.join(picdir, 'Font.ttc')
        
        if not EPD_AVAILABLE:
            self.logger.warning("墨水屏驱动不可用，将使用模拟模式")
            return
            
        try:
            self.epd = epd3in52.EPD()
            self.logger.info("墨水屏控制器初始化成功")
        except Exception as e:
            self.logger.error(f"墨水屏初始化失败: {e}")
            self.epd = None
    
    def _get_fonts(self):
        """获取字体对象"""
        try:
            font24 = ImageFont.truetype(self.font_path, 24)
            font18 = ImageFont.truetype(self.font_path, 18)
            font12 = ImageFont.truetype(self.font_path, 12)
            return font24, font18, font12
        except Exception as e:
            self.logger.warning(f"字体加载失败，使用默认字体: {e}")
            return ImageFont.load_default(), ImageFont.load_default(), ImageFont.load_default()
    
    def display_daily_content(self, content):
        """显示每日内容到墨水屏"""
        if not self.epd:
            self.logger.warning("墨水屏不可用，跳过显示")
            return False
            
        try:
            # 初始化墨水屏
            self.epd.init()
            self.epd.Clear()
            
            # 创建图像
            image = Image.new('1', (self.epd.width, self.epd.height), 255)
            draw = ImageDraw.Draw(image)
            
            # 获取字体
            font24, font18, font12 = self._get_fonts()
            
            # 获取IP地址
            try:
                ipaddress = get_ipaddress.get_ip_address()
            except:
                ipaddress = "N/A"
            
            # 绘制标题
            draw.text((10, 10), "Daily Word & Sentence", font=font18, fill=0)
            
            # 绘制时间
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            draw.text((10, 35), f"Time: {current_time}", font=font12, fill=0)
            
            y_pos = 70
            
            # 绘制每日单词
            if 'word' in content:
                word_data = content['word']
                draw.text((10, y_pos), "Daily Word:", font=font18, fill=0)
                y_pos += 25
                
                # 单词
                word_text = f"Word: {word_data.get('word', 'N/A')}"
                draw.text((10, y_pos), word_text, font=font24, fill=0)
                y_pos += 30
                
                # 音标
                if 'phonetic' in word_data:
                    phonetic_text = f"Phonetic: {word_data['phonetic']}"
                    draw.text((10, y_pos), phonetic_text, font=font12, fill=0)
                    y_pos += 20
                
                # 释义
                if 'meaning' in word_data:
                    meaning_text = f"Meaning: {word_data['meaning']}"
                    # 使用文本换行
                    try:
                        wrapped_meaning = text_wrap.format_poem_for_display(meaning_text, 350)
                        draw.text((10, y_pos), wrapped_meaning, font=font12, fill=0)
                    except:
                        draw.text((10, y_pos), meaning_text[:50] + "...", font=font12, fill=0)
                    y_pos += 40
            
            # 绘制每日句子
            if 'sentence' in content:
                sentence_data = content['sentence']
                draw.text((10, y_pos), "Daily Sentence:", font=font18, fill=0)
                y_pos += 25
                
                sentence_text = sentence_data.get('sentence', 'N/A')
                try:
                    wrapped_sentence = text_wrap.format_poem_for_display(sentence_text, 350)
                    draw.text((10, y_pos), wrapped_sentence, font=font18, fill=0)
                except:
                    # 简单换行处理
                    words = sentence_text.split()
                    lines = []
                    current_line = ""
                    for word in words:
                        if len(current_line + word) < 40:
                            current_line += word + " "
                        else:
                            lines.append(current_line.strip())
                            current_line = word + " "
                    if current_line:
                        lines.append(current_line.strip())
                    
                    for line in lines[:3]:  # 最多显示3行
                        draw.text((10, y_pos), line, font=font18, fill=0)
                        y_pos += 22
                
                y_pos += 20
            
            # 显示IP地址
            draw.text((10, self.epd.height - 30), f"IP: {ipaddress}", font=font12, fill=0)
            
            # 显示到墨水屏
            self.epd.display(self.epd.getbuffer(image))
            self.epd.refresh()
            time.sleep(2)
            self.epd.sleep()
            
            self.logger.info("内容已成功显示到墨水屏")
            return True
            
        except Exception as e:
            self.logger.error(f"墨水屏显示失败: {e}")
            return False
    
    def clear_display(self):
        """清空墨水屏显示"""
        if not self.epd:
            return False
            
        try:
            self.epd.init()
            self.epd.Clear()
            self.epd.sleep()
            self.logger.info("墨水屏已清空")
            return True
        except Exception as e:
            self.logger.error(f"清空墨水屏失败: {e}")
            return False
    
    def test_display(self):
        """测试墨水屏显示"""
        test_content = {
            'word': {
                'word': 'example',
                'phonetic': '/ɪɡˈzæmpl/',
                'meaning': 'a thing characteristic of its kind or illustrating a general rule'
            },
            'sentence': {
                'sentence': 'This is an example sentence for testing the e-paper display functionality.'
            }
        }
        
        self.logger.info("开始墨水屏测试显示...")
        result = self.display_daily_content(test_content)
        
        if result:
            self.logger.info("墨水屏测试显示成功")
        else:
            self.logger.error("墨水屏测试显示失败")
            
        return result
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.epd:
                self.epd.sleep()
            self.logger.info("墨水屏资源已清理")
        except Exception as e:
            self.logger.warning(f"清理墨水屏资源时出错: {e}")


def main():
    """主函数 - 用于测试"""
    logging.basicConfig(level=logging.INFO)
    
    controller = DailyWordEPaperController()
    controller.test_display()


if __name__ == "__main__":
    main()