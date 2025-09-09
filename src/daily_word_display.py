#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
每日单词墨水屏显示程序
适用于树莓派 + 墨水屏的每日单词和励志句子显示
"""

import sys
import time
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent))

from class_word_api import WordAPI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_word.log'),
        logging.StreamHandler()
    ]
)


class DailyWordDisplay:
    """每日单词显示控制器"""
    
    def __init__(self):
        """初始化显示控制器"""
        self.word_api = WordAPI()
        self.display_width = 400  # 墨水屏宽度
        self.display_height = 300  # 墨水屏高度
        
    def update_display(self):
        """更新墨水屏显示内容"""
        try:
            logging.info("开始更新每日单词显示...")
            
            # 获取每日内容
            success = self.word_api.get_daily_content()
            
            if not success:
                logging.error("获取每日内容失败")
                return False
            
            # 获取格式化内容
            content = self.word_api.format_display_content()
            
            # 这里应该调用实际的墨水屏显示函数
            # 由于没有实际的墨水屏硬件，我们先打印到控制台
            self._display_to_console(content)
            
            # 如果有实际的墨水屏，可以调用类似这样的函数：
            # self._display_to_epaper(content)
            
            logging.info("成功更新每日单词显示")
            return True
            
        except Exception as e:
            logging.error(f"更新显示时出错: {e}")
            return False
    
    def _display_to_console(self, content):
        """在控制台显示内容（用于测试）"""
        print("\n" + "="*60)
        print("墨水屏显示内容预览:")
        print("="*60)
        print(content)
        print("="*60)
    
    def _display_to_epaper(self, content):
        """
        在实际墨水屏上显示内容
        这个函数需要根据具体的墨水屏库来实现
        """
        # 示例代码框架（需要根据实际硬件调整）
        try:
            # import epd2in7  # 假设使用2.7寸墨水屏
            # from PIL import Image, ImageDraw, ImageFont
            
            # # 初始化墨水屏
            # epd = epd2in7.EPD()
            # epd.init()
            # epd.Clear(0xFF)
            
            # # 创建图像
            # image = Image.new('1', (self.display_width, self.display_height), 255)
            # draw = ImageDraw.Draw(image)
            
            # # 设置字体
            # font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
            
            # # 绘制文本
            # lines = content.split('\n')
            # y_position = 10
            # for line in lines:
            #     if y_position < self.display_height - 20:
            #         draw.text((10, y_position), line, font=font, fill=0)
            #         y_position += 15
            
            # # 显示图像
            # epd.display(epd.getbuffer(image))
            # epd.sleep()
            
            logging.info("内容已显示到墨水屏")
            
        except Exception as e:
            logging.error(f"墨水屏显示出错: {e}")
    
    def run_daily_update(self):
        """执行每日更新"""
        logging.info("开始每日单词更新任务")
        
        max_retries = 3
        for attempt in range(max_retries):
            if self.update_display():
                logging.info("每日更新完成")
                return True
            else:
                logging.warning(f"更新失败，重试 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(30)  # 等待30秒后重试
        
        logging.error("多次重试后仍然失败")
        return False


def main():
    """主函数"""
    try:
        display = DailyWordDisplay()
        
        # 检查命令行参数
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            # 测试模式
            print("运行测试模式...")
            display.update_display()
        else:
            # 正常运行模式
            display.run_daily_update()
            
    except KeyboardInterrupt:
        logging.info("程序被用户中断")
    except Exception as e:
        logging.error(f"程序运行出错: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())