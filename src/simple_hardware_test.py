#!/usr/bin/env python3
"""
Simple Hardware Test for E-paper Display
Tests the basic hardware functionality
"""

import sys
import os
import time
import logging

# Add e-paper library path
sys.path.insert(0, os.path.expanduser("~/e-Paper/RaspberryPi_JetsonNano/python/lib"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_hardware():
    """Test basic e-paper hardware functionality"""

    try:
        logger.info("🔧 Importing e-paper library...")
        import waveshare_epd.epd3in52 as epd3in52
        logger.info("✅ Waveshare e-paper library imported successfully")

        logger.info("🖼️ Creating EPD driver object...")
        epd = epd3in52.EPD()
        logger.info("✅ EPD 3.52-inch driver object created")

        logger.info("⚡ Initializing e-paper hardware...")
        epd.init()
        logger.info("✅ E-paper hardware initialized successfully")

        logger.info("🧹 Clearing display...")
        epd.Clear()
        logger.info("✅ Display cleared successfully")

        logger.info("😴 Putting display to sleep...")
        epd.sleep()
        logger.info("✅ Display put to sleep successfully")

        return True

    except Exception as e:
        logger.error(f"❌ Hardware test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple E-paper Hardware Test")
    print("=" * 40)

    success = test_basic_hardware()

    if success:
        print("✅ Basic hardware test completed successfully!")
        print("Your e-paper display is working correctly.")
    else:
        print("❌ Basic hardware test failed!")
        print("Check your hardware connections and try again.")