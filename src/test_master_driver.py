#!/usr/bin/env python3
"""
基于Master分支可工作版本的测试脚本
Working Test Script Based on Master Branch
"""

import os
import sys
import time
import logging
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to use hardware
try:
    import spidev
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
    logger.info("✅ Hardware libraries available")
except ImportError:
    HARDWARE_AVAILABLE = False
    logger.warning("⚠️ Hardware libraries not available, simulation mode")

class EPDConfig:
    """E-Paper Configuration from Master Branch"""

    def __init__(self):
        # GPIO引脚配置 - Master分支的配置
        self.RST_PIN = 17      # Reset
        self.DC_PIN = 25       # Data/Command
        self.CS_PIN = 8        # Chip Select
        self.BUSY_PIN = 24     # Busy

        # SPI配置
        self.SPI_BUS = 0
        self.SPI_DEVICE = 0
        self.SPI_SPEED = 4000000  # 4MHz

        if HARDWARE_AVAILABLE:
            self._init_gpio()
            logger.info("✅ GPIO initialized with Master branch config")

    def _init_gpio(self):
        """Initialize GPIO"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        GPIO.setup(self.BUSY_PIN, GPIO.IN)

    def module_exit(self, cleanup=True):
        """Cleanup module resources"""
        if HARDWARE_AVAILABLE and cleanup:
            GPIO.cleanup()

# Global configuration instance
epdconfig = EPDConfig()

class EPD3in52:
    """3.52-inch E-Paper Driver from Master Branch"""

    def __init__(self):
        self.width = 360
        self.height = 240
        self.WHITE = 0xFF
        self.BLACK = 0x00

        if HARDWARE_AVAILABLE:
            self.spi = spidev.SpiDev()
            logger.info("✅ SPI initialized")

    def init(self):
        """Initialize display using Master branch method"""
        if not HARDWARE_AVAILABLE:
            logger.info("🖥️ Simulation mode: E-Paper initialization")
            return

        try:
            # Open SPI - Master branch method
            self.spi.open(epdconfig.SPI_BUS, epdconfig.SPI_DEVICE)
            self.spi.max_speed_hz = epdconfig.SPI_SPEED
            self.spi.mode = 0b00

            logger.info(f"📡 SPI opened: bus={epdconfig.SPI_BUS}, device={epdconfig.SPI_DEVICE}")
            logger.info(f"⚡ SPI speed: {epdconfig.SPI_SPEED} Hz")

            # Reset display - Master branch method
            self.reset()
            self.wait_until_idle()

            logger.info("✅ E-Paper initialized using Master branch method")
            return True
        except Exception as e:
            logger.error(f"❌ E-Paper initialization failed: {e}")
            return False

    def reset(self):
        """Reset display using Master branch method"""
        if not HARDWARE_AVAILABLE:
            logger.info("🖥️ Simulation mode: Reset")
            return

        logger.info("🔄 Resetting display...")
        GPIO.output(epdconfig.RST_PIN, 1)
        time.sleep(0.2)
        GPIO.output(epdconfig.RST_PIN, 0)
        time.sleep(0.002)
        GPIO.output(epdconfig.RST_PIN, 1)
        time.sleep(0.2)
        logger.info("✅ Reset complete")

    def wait_until_idle(self):
        """Wait until display is idle"""
        if not HARDWARE_AVAILABLE:
            return

        logger.info("⏳ Waiting for display to be ready...")
        count = 0
        while GPIO.input(epdconfig.BUSY_PIN) == 1:
            time.sleep(0.01)
            count += 1
            if count > 1000:  # 10 second timeout
                logger.warning("⚠️ Display busy timeout")
                break
        logger.info("✅ Display ready")

    def send_command(self, command):
        """Send command - Master branch method"""
        if not HARDWARE_AVAILABLE:
            logger.info(f"🖥️ Simulation mode: Send command 0x{command:02X}")
            return

        GPIO.output(epdconfig.DC_PIN, 0)  # Command mode
        GPIO.output(epdconfig.CS_PIN, 0)   # Chip select active
        self.spi.writebytes([command])
        GPIO.output(epdconfig.CS_PIN, 1)   # Chip select inactive

    def send_data(self, data):
        """Send data - Master branch method"""
        if not HARDWARE_AVAILABLE:
            return

        GPIO.output(epdconfig.DC_PIN, 1)  # Data mode
        GPIO.output(epdconfig.CS_PIN, 0)   # Chip select active
        self.spi.writebytes([data])
        GPIO.output(epdconfig.CS_PIN, 1)   # Chip select inactive

    def Clear(self):
        """Clear display using Master branch method"""
        if not HARDWARE_AVAILABLE:
            logger.info("🖥️ Simulation mode: Clear display")
            return

        logger.info("🧹 Clearing display...")

        # Send clear command
        self.send_command(0x10)  # DATA_START_TRANSMISSION_1
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(self.WHITE)  # White screen

        # Refresh display
        self.refresh()
        logger.info("✅ Display cleared")

    def refresh(self):
        """Refresh display - Master branch method"""
        if not HARDWARE_AVAILABLE:
            logger.info("🖥️ Simulation mode: Refresh display")
            return

        logger.info("🔄 Refreshing display...")
        self.send_command(0x12)  # DISPLAY_REFRESH
        self.wait_until_idle()
        logger.info("✅ Display refreshed")

    def display(self, image_buffer):
        """Display image - Master branch method"""
        if not HARDWARE_AVAILABLE:
            logger.info("🖥️ Simulation mode: Display image")
            return

        logger.info("📺 Displaying image...")
        self.send_command(0x13)  # DATA_START_TRANSMISSION_2
        for byte in image_buffer:
            self.send_data(byte)

        # Refresh after sending data
        self.refresh()
        logger.info("✅ Image displayed")

    def getbuffer(self, image):
        """Get image buffer - Master branch method"""
        if image.mode != '1':
            image = image.convert('1')

        # Convert image to byte array
        buf = []
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size

        if imwidth != self.width or imheight != self.height:
            logger.info(f"🔄 Resizing image from {imwidth}x{imheight} to {self.width}x{self.height}")
            image_monocolor = image_monocolor.resize((self.width, self.height))

        pixels = list(image_monocolor.getdata())

        for i in range(0, len(pixels), 8):
            byte = 0
            for j in range(8):
                if i + j < len(pixels):
                    if pixels[i + j] == 0:  # Black pixel
                        byte |= (1 << (7 - j))
            buf.append(byte)

        return buf

    def sleep(self):
        """Enter sleep mode - Master branch method"""
        if not HARDWARE_AVAILABLE:
            logger.info("🖥️ Simulation mode: Sleep")
            return

        logger.info("😴 Entering sleep mode...")
        self.send_command(0x02)  # POWER_OFF
        self.wait_until_idle()
        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)

        if hasattr(self, 'spi'):
            self.spi.close()
        logger.info("✅ Sleep mode activated")

def test_master_branch_driver():
    """Test using Master branch driver method"""

    print("🚀 Master Branch Driver Test")
    print("=" * 50)
    print("This uses the driver from the working 2024 version")
    print("=" * 50)

    try:
        # Initialize display using Master branch method
        logger.info("🖼️ Initializing EPD using Master branch method...")
        epd = EPD3in52()

        if not epd.init():
            logger.error("❌ Failed to initialize display")
            return False

        width, height = epd.width, epd.height
        logger.info(f"📐 Display size: {width}x{height}")

        # Test 1: Clear screen
        logger.info("⚪ Test 1: Clear screen (white)...")
        epd.Clear()
        time.sleep(3)

        # Test 2: Simple black screen
        logger.info("⚫ Test 2: Black screen...")
        black_image = Image.new('1', (width, height), 0)  # All black
        epd.display(epd.getbuffer(black_image))
        time.sleep(3)

        # Test 3: Half and half
        logger.info("⚫⚪ Test 3: Half black, half white...")
        half_image = Image.new('1', (width, height), 255)  # White background
        draw = ImageDraw.Draw(half_image)
        draw.rectangle([0, 0, width//2, height], fill=0)  # Left half black
        epd.display(epd.getbuffer(half_image))
        time.sleep(3)

        # Test 4: Simple text
        logger.info("📝 Test 4: Simple text...")
        text_image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(text_image)

        # Use default font
        font = ImageFont.load_default()
        draw.text((10, 10), "MASTER BRANCH", font=font, fill=0)
        draw.text((10, 30), "DRIVER TEST", font=font, fill=0)
        draw.text((10, 50), "If you can see", font=font, fill=0)
        draw.text((10, 70), "this text, the", font=font, fill=0)
        draw.text((10, 90), "Master branch", font=font, fill=0)
        draw.text((10, 110), "driver works!", font=font, fill=0)

        epd.display(epd.getbuffer(text_image))
        time.sleep(5)

        # Save test images
        black_image.save('master_test_black.png')
        half_image.save('master_test_half.png')
        text_image.save('master_test_text.png')
        logger.info("💾 Test images saved")

        # Cleanup
        logger.info("😴 Putting display to sleep...")
        epd.sleep()

        if HARDWARE_AVAILABLE:
            epdconfig.module_exit(cleanup=True)

        logger.info("✅ Master branch driver test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Master branch driver test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_master_branch_driver()

    if success:
        print("\n✅ SUCCESS! Master branch driver works!")
        print("If you could see clear patterns and text, the issue was the driver method.")
    else:
        print("\n❌ Test failed! Check error messages above.")