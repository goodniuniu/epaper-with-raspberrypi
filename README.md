# E-paper Weather & Poetry Display for Raspberry Pi

A modern Python application that displays weather information and Chinese poetry on a 3.52-inch e-paper display using Raspberry Pi.

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Last Updated](https://img.shields.io/badge/updated-2025--11--18-informational.svg)

## Features

✅ **Real-time Weather Information** - Fetches current weather data using WeatherAPI
✅ **Chinese Poetry Display** - Retrieves daily classical Chinese poetry from Jinrishici API
✅ **Network Information** - Shows Raspberry Pi IP address for remote access
✅ **E-paper Display** - 3.52-inch e-ink screen optimized output
✅ **Modern Codebase** - Type hints, proper error handling, and logging
✅ **Object-Oriented Design** - Clean, maintainable architecture

## Project Structure

```
epaper-with-raspberrypi/
├── src/                          # Main source code
│   ├── main.py                   # Main application entry point
│   ├── get_weather.py            # Weather API integration
│   ├── class_poem_api.py         # Poetry API class
│   ├── get_config.py             # Configuration management
│   ├── get_ipaddress.py          # Network utilities
│   └── process_*.py              # Data processing utilities
├── tmp/                          # Testing and development files
├── config.ini                    # Configuration file
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Quick Start

### Prerequisites

- Raspberry Pi (3B+ or newer recommended)
- 3.52-inch e-paper display (Waveshare EPD 3in52)
- Python 3.8+ installed
- Internet connection for API access

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/epaper-with-raspberrypi.git
   cd epaper-with-raspberrypi
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys:**
   Edit `config.ini`:
   ```ini
   [DEFAULT]
   # Get your API key from https://www.weatherapi.com/
   WEATHER_API_KEY = your_api_key_here
   CITY_API_KEY = YOUR_CITY_NAME

   # Poetry API URLs (no key required)
   POEM_TOKEN_API_URL = https://v2.jinrishici.com/token
   DAILY_POEM_API_URL = https://v2.jinrishici.com/sentence
   ```

4. **Run the application:**
   ```bash
   cd src
   python main.py
   ```

## API Setup

### Weather API
1. Register at [WeatherAPI.com](https://www.weatherapi.com/)
2. Get your free API key
3. Add it to `config.ini` as `WEATHER_API_KEY`

### Poetry API
- Uses Jinrishici API (free, no registration required)
- Automatically handled by the application

## Configuration

The application is configured through `config.ini`:

```ini
[DEFAULT]
# Weather API configuration
WEATHER_API_KEY = your_weather_api_key
CITY_API_KEY = YourCityName

# Poetry API URLs
POEM_TOKEN_API_URL = https://v2.jinrishici.com/token
DAILY_POEM_API_URL = https://v2.jinrishici.com/sentence
```

## Development & Updates

### Recent Updates (2025-11-18)
- ✅ Updated all dependencies to latest versions
- ✅ Added comprehensive type hints throughout
- ✅ Improved error handling with proper logging
- ✅ Removed hardcoded API keys for security
- ✅ Modernized code structure with docstrings
- ✅ Cleaned up duplicate and deprecated code
- ✅ Enhanced configuration management

### Code Quality
- **Type Safety:** Full type hints support
- **Error Handling:** Comprehensive exception management
- **Logging:** Structured logging with multiple handlers
- **Documentation:** Complete docstring coverage
- **Security:** No hardcoded secrets

## Hardware Setup

### E-paper Display Connection
1. Connect the 3.52-inch e-paper display to Raspberry Pi GPIO pins
2. Ensure proper power and data connections
3. Install Waveshare e-paper library (included in requirements)

### GPIO Pinout
Refer to the Waveshare EPD 3in52 documentation for specific pin connections.

## Troubleshooting

### Common Issues

1. **Display not working:**
   - Check GPIO connections
   - Verify e-paper library installation
   - Check for permission issues with I2C/SPI

2. **API errors:**
   - Verify internet connection
   - Check API key validity
   - Review configuration file

3. **Permission denied errors:**
   ```bash
   sudo chmod +x src/main.py
   ```

## Development History

### Original Development (2024)
- **Feb 15, 2024:** Object-oriented refactoring of poetry module
- **Feb 16, 2024:** E-paper display integration and SQLite database support

### Modern Update (2025-11-18)
- Complete codebase modernization
- Security improvements
- Enhanced error handling
- Updated dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Credits

- Weather data from [WeatherAPI](https://www.weatherapi.com/)
- Poetry from [Jinrishici API](https://www.jinrishici.com/)
- E-paper library by [Waveshare](https://www.waveshare.com/)

---

**Note:** This project was originally developed with AI assistance and has been updated to modern development standards in 2025.
