#!/usr/bin/env python3
"""
简化的 Waveshare E-Paper 驱动模块
Simplified Waveshare E-Paper driver module based on example code
"""

import os
import sys
import time
import logging
from PIL import Image, ImageDraw, ImageFont

try:
    import spidev
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    print("警告: 硬件库未安装，运行在模拟模式")

class EPDConfig:
    """E-Paper 配置类"""
    
    def __init__(self):
        # GPIO 引脚配置
        self.RST_PIN = 17
        self.DC_PIN = 25
        self.CS_PIN = 8
        self.BUSY_PIN = 24
        
        # SPI 配置
        self.SPI_BUS = 0
        self.SPI_DEVICE = 0
        self.SPI_SPEED = 4000000
        
        if HARDWARE_AVAILABLE:
            self._init_gpio()
    
    def _init_gpio(self):
        """初始化GPIO"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        GPIO.setup(self.BUSY_PIN, GPIO.IN)
    
    def module_exit(self, cleanup=True):
        """清理模块资源"""
        if HARDWARE_AVAILABLE and cleanup:
            GPIO.cleanup()

# 全局配置实例
epdconfig = EPDConfig()

class EPD3in52:
    """3.52英寸 E-Paper 显示器驱动"""
    
    def __init__(self):
        self.width = 360
        self.height = 240
        self.WHITE = 0xFF
        self.BLACK = 0x00
        
        if HARDWARE_AVAILABLE:
            self.spi = spidev.SpiDev()
    
    def init(self):
        """初始化显示器"""
        if not HARDWARE_AVAILABLE:
            logging.info("模拟模式：E-Paper 初始化")
            return
        
        try:
            # 打开SPI
            self.spi.open(epdconfig.SPI_BUS, epdconfig.SPI_DEVICE)
            self.spi.max_speed_hz = epdconfig.SPI_SPEED
            self.spi.mode = 0b00
            
            # 重置显示器
            self.reset()
            self.wait_until_idle()
            
            logging.info("E-Paper 初始化完成")
        except Exception as e:
            logging.error(f"E-Paper 初始化失败: {e}")
    
    def reset(self):
        """重置显示器"""
        if not HARDWARE_AVAILABLE:
            return
        
        GPIO.output(epdconfig.RST_PIN, 1)
        time.sleep(0.2)
        GPIO.output(epdconfig.RST_PIN, 0)
        time.sleep(0.002)
        GPIO.output(epdconfig.RST_PIN, 1)
        time.sleep(0.2)
    
    def wait_until_idle(self):
        """等待显示器空闲"""
        if not HARDWARE_AVAILABLE:
            return
        
        while GPIO.input(epdconfig.BUSY_PIN) == 1:
            time.sleep(0.01)
    
    def send_command(self, command):
        """发送命令"""
        if not HARDWARE_AVAILABLE:
            return
        
        GPIO.output(epdconfig.DC_PIN, 0)
        GPIO.output(epdconfig.CS_PIN, 0)
        self.spi.writebytes([command])
        GPIO.output(epdconfig.CS_PIN, 1)
    
    def send_data(self, data):
        """发送数据"""
        if not HARDWARE_AVAILABLE:
            return
        
        GPIO.output(epdconfig.DC_PIN, 1)
        GPIO.output(epdconfig.CS_PIN, 0)
        self.spi.writebytes([data])
        GPIO.output(epdconfig.CS_PIN, 1)
    
    def display_NUM(self, color):
        """清屏"""
        if not HARDWARE_AVAILABLE:
            logging.info(f"模拟模式：清屏 (颜色: {color})")
            return
        
        # 发送清屏命令
        self.send_command(0x10)  # DATA_START_TRANSMISSION_1
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(color)
    
    def Clear(self):
        """清空显示"""
        self.display_NUM(self.WHITE)
        if HARDWARE_AVAILABLE:
            self.refresh()
    
    def lut_GC(self):
        """加载灰度查找表"""
        if not HARDWARE_AVAILABLE:
            return
        
        # 简化的LUT设置
        self.send_command(0x20)  # LUT_FOR_VCOM
        # 这里应该发送实际的LUT数据，简化处理
    
    def refresh(self):
        """刷新显示"""
        if not HARDWARE_AVAILABLE:
            logging.info("模拟模式：刷新显示")
            return
        
        self.send_command(0x12)  # DISPLAY_REFRESH
        self.wait_until_idle()
    
    def display(self, image_buffer):
        """显示图像"""
        if not HARDWARE_AVAILABLE:
            logging.info("模拟模式：显示图像")
            return
        
        self.send_command(0x13)  # DATA_START_TRANSMISSION_2
        for byte in image_buffer:
            self.send_data(byte)
    
    def getbuffer(self, image):
        """获取图像缓冲区"""
        if image.mode != '1':
            image = image.convert('1')
        
        # 转换图像为字节数组
        buf = []
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        
        if imwidth != self.width or imheight != self.height:
            image_monocolor = image_monocolor.resize((self.width, self.height))
        
        pixels = list(image_monocolor.getdata())
        
        for i in range(0, len(pixels), 8):
            byte = 0
            for j in range(8):
                if i + j < len(pixels):
                    if pixels[i + j] == 0:  # 黑色像素
                        byte |= (1 << (7 - j))
            buf.append(byte)
        
        return buf
    
    def sleep(self):
        """进入睡眠模式"""
        if not HARDWARE_AVAILABLE:
            logging.info("模拟模式：进入睡眠")
            return
        
        self.send_command(0x02)  # POWER_OFF
        self.wait_until_idle()
        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)
        
        if hasattr(self, 'spi'):
            self.spi.close()

# 创建模块级别的类实例
class epd3in52:
    """模块级别的EPD类"""
    EPD = EPD3in52
    epdconfig = epdconfig

# 为了兼容性，也创建直接的类引用
EPD = EPD3in52