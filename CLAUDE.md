# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Raspberry Pi e-paper display system that shows real-time weather information and Chinese classical poetry on a 3.52-inch Waveshare e-paper display. The project has been completely modernized (2025-11-18) with object-oriented architecture, comprehensive error handling, and type safety.

## Quick Start Commands

### Main Application
```bash
# Easy runner script (recommended)
./run_display.sh

# Manual execution with display
cd src
export PYTHONPATH="$HOME/e-Paper/RaspberryPi_JetsonNano/python/lib:$PYTHONPATH"
python main_with_display.py

# Console only (for testing)
cd src
python main.py
```

### Testing
```bash
# Run basic display test
cd src
python basic_display_test.py

# Run hardware diagnostics
cd src
python hardware_test.py

# Test specific components
python font_rendering_test.py
python optimized_display_test.py
```

## Architecture

### Core Components
- **`src/main.py`** - Data fetching console application
- **`src/main_with_display.py`** - Full application with e-paper display
- **`src/get_weather.py`** - WeatherAPI.com integration
- **`src/class_poem_api.py`** - Object-oriented poetry API client
- **`src/get_config.py`** - Configuration management

### Hardware Integration
- **Display**: 3.52-inch Waveshare e-paper (240x360 pixels)
- **Interface**: SPI communication with GPIO control
- **Library**: Waveshare e-paper library (`waveshare_epd.epd3in52`)
- **Dependencies**: RPi.GPIO, spidev, Pillow/PIL

### Data Flow
1. Configuration loading from `config.ini`
2. API calls to WeatherAPI.com and Jinrishici.com
3. Text processing and Chinese font rendering
4. Image generation using PIL
5. SPI transmission to e-paper display

## Configuration

### Main Configuration
- **`config.ini`** - Contains API keys and settings
- **`requirements.txt`** - Python dependencies
- **Environment**: Requires `PYTHONPATH` for e-paper library

### Critical Settings
```ini
[DEFAULT]
WEATHER_API_KEY = [key from config.ini]
CITY_API_KEY = GUANGZHOU
POEM_TOKEN_API_URL = https://v2.jinrishici.com/token
DAILY_POEM_API_URL = https://v2.jinrishici.com/sentence
```

### Hardware Requirements
- **Power**: 5V 2A external power adapter (critical for stability)
- **GPIO**: Specific pin mapping for SPI control
- **Fonts**: WQY Zenhei/Microhei for Chinese character support

## Development Patterns

### Error Handling
- Network timeouts for all API calls
- Hardware initialization retry logic
- Font loading with multiple fallbacks
- Comprehensive logging to file and console

### Performance Characteristics
- **Total Runtime**: ~8-10 seconds
- **Memory Usage**: <50MB
- **Display Refresh**: 3-5 seconds
- **Initialization**: ~2 seconds

### Code Standards
- Full type hints implementation
- Object-oriented design with proper separation of concerns
- Externalized configuration (no hardcoded secrets)
- Comprehensive test coverage (20+ test files)

## Testing Strategy

### Test Categories
- **Hardware Tests** - Display functionality, SPI communication
- **API Tests** - Weather and poetry data fetching
- **Integration Tests** - Full system testing
- **Performance Tests** - Timing and memory usage

### Key Test Files
- `basic_display_test.py` - Core display functionality
- `hardware_test.py` - Hardware diagnostics
- `font_rendering_test.py` - Chinese character rendering
- `optimized_display_test.py` - Performance testing

## Troubleshooting

### Common Issues
- **Power Problems**: Use external 5V 2A power supply
- **Display Artifacts**: Check SPI connections and power supply
- **Chinese Font Issues**: Install WQY fonts: `sudo apt-get install fonts-wqy-zenhei`
- **SPI Permissions**: Ensure user has GPIO and SPI access

### Documentation Files
- **`DISPLAY_DIAGNOSIS.md`** - Hardware testing results
- **`STRIPES_SOLUTION.md`** - Display troubleshooting guide
- **`CHANGELOG.md`** - Detailed development history

## Security Notes

- API keys externalized in `config.ini` (not in source code)
- Poetry API token management implemented
- GPIO and SPI device access permissions required
- Claude Code permissions configured in `.claude/settings.local.json`