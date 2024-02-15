#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

# 定义图像和库的路径
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')

# 如果lib路径存在，则添加到系统路径中，以便导入waveshare_epd库
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd3in52  # 导入waveshare电子墨水屏库
import time
from PIL import Image, ImageDraw, ImageFont  # 导入PIL库进行图像处理
import traceback

# 配置日志记录级别为DEBUG，便于调试
logging.basicConfig(level=logging.DEBUG)

try:
    # 初始化电子墨水屏并清屏
    logging.info("epd3in52 Demo")
    epd = epd3in52.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.display_NUM(epd.WHITE)  # 清屏
    epd.lut_GC()  # 加载灰度显示查找表
    epd.refresh()
    epd.send_command(0x50)  # 发送命令调整屏幕设置
    epd.send_data(0x17)  # 发送数据
    time.sleep(2)  # 等待2秒，让屏幕刷新

    # 加载字体
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)
    
    # 绘制横向图像
    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new('1', (epd.height, epd.width), 255)  # 创建白色背景图像
    draw = ImageDraw.Draw(Himage)  # 创建一个可以在Himage上绘图的对象
    draw.text((10, 0), 'hello world', font=font24, fill=0)
    draw.text((10, 20), '3.52inch e-Paper', font=font24, fill=0)
    draw.text((150, 0), u'微雪电子', font=font24, fill=0)    
    draw.line((20, 50, 70, 100), fill=0)
    draw.line((70, 50, 20, 100), fill=0)
    draw.rectangle((20, 50, 70, 100), outline=0)
    draw.line((165, 50, 165, 100), fill=0)
    draw.line((140, 75, 190, 75), fill=0)
    draw.arc((140, 50, 190, 100), 0, 360, fill=0)
    draw.rectangle((80, 50, 130, 100), fill=0)
    draw.chord((200, 50, 250, 100), 0, 360, fill=0)
    epd.display(epd.getbuffer(Himage))  # 显示图像
    epd.lut_GC()  # 加载灰度显示查找表
    epd.refresh()
    time.sleep(2)
    
    # 绘制纵向图像
    logging.info("2.Drawing on the Vertical image...")
    Limage = Image.new('1', (epd.width, epd.height), 255)  # 创建纵向的白色背景图像
    draw = ImageDraw.Draw(Limage)
    draw.text((2, 0), 'hello world', font=font18, fill=0)
    draw.text((2, 20), '3.52inch e-Paper', font=font18, fill=0)
    draw.text((20, 50), u'微雪电子', font=font18, fill=0)
    draw.line((10, 90, 60, 140), fill=0)
    draw.line((60, 90, 10, 140), fill=0)
    draw.rectangle((10, 90, 60, 140), outline=0)
    draw.line((95, 90, 95, 140), fill=0)
    draw.line((70, 115, 120, 115), fill=0)
    draw.arc((70, 90, 120, 140), 0, 360, fill=0)
    draw.rectangle((10, 150, 60, 200), fill=0)
    draw.chord((70, 150, 120, 200), 0, 360, fill=0)
    epd.display(epd.getbuffer(Limage))  # 显示图像
    epd.lut_GC()  # 加载灰度显示查找表
    epd.refresh()
    time.sleep(2)
    
    # 读取并显示位图文件
    logging.info("3.read bmp file")
    Himage = Image.open(os.path.join(picdir, '3in52-1.bmp'))
    epd.display(epd.getbuffer(Himage))
    epd.lut_GC()
    epd.refresh()
    time.sleep(2)
    
    # 在指定窗口显示位图文件
    logging.info("4.read bmp file on window")
    Himage2 = Image.new('1', (epd.height, epd.width), 255)
    bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
    Himage2.paste(bmp, (50,10))
    epd.display(epd.getbuffer(Himage2))
    epd.lut_GC()
    epd.refresh()
    time.sleep(2)

    # 清除屏幕并进入休眠模式
    logging.info("Clear...")
    epd.Clear()
    
    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd3in52.epdconfig.module_exit(cleanup=True)
    exit()
