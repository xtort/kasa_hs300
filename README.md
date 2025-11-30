# TP-Link HS300 Power Strip CLI
# VERSION 1.0a

A command-line interface for controlling TP-Link HS300 Smart Power Strip outlets. This tool provides an intuitive menu-driven system to view the status of all outlets and control individual outlets.

## Features

- **Menu-driven interface**: Easy-to-use CLI with clear menus and options
- **Real-time status**: View the current status of all outlets at once
- **Individual control**: Turn individual outlets on/off
- **Configurable IP**: Easy configuration of power strip IP address
- **Error handling**: Robust error handling with user-friendly messages
- **Visual indicators**: Emoji indicators for outlet status (🟢 ON, 🔴 OFF)
- **Outlet Names**: Names are pulled directly from the power strip, set them using the mobile Kasa app

## Requirements

- Python 3.7 or higher
- TP-Link HS300 Smart Power Strip
- Network connectivity to the power strip

## Installation

### Option 1: Direct Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Run the CLI directly:

```bash
python src/kasa_cli.py --ip 192.168.2.3 # replace this with the correct ip address of the hs300
```

### Option 2: Install as Package

```bash
pip install -e .
```

Then run:

```bash
kasa-cli --ip 192.168.2.3 # replace this with the correct ip address of the hs300
```

## Configuration

### IP Address Configuration

You can configure the power strip IP address in several ways:

1. **Command line argument** (recommended):
   ```bash
   python src/kasa_cli.py --ip 192.168.2.3 # replace this with the correct ip address of the hs300
   ```

2. **Edit config.py**:
   ```python
   POWER_STRIP_IP = "192.168.2.3" # replace this with the correct ip address of the hs300
   ```

3. **Default fallback**: If no IP is specified, it defaults to `192.168.2.3` 

## Usage

### Starting the CLI

```bash
# Using default IP (192.168.2.3)
python src/kasa_cli.py

# Using custom IP
python src/kasa_cli.py --ip 192.168.1.100

# Using installed package
kasa-cli --ip 192.168.1.100
```

### Main Menu

The main menu displays:
- Power strip IP address and device name
- Status of all outlets with visual indicators
- Menu options

```
============================================================
           TP-Link HS300 Power Strip Controller
============================================================

Power Strip IP: 192.168.2.3
Device Name: My Power Strip

Outlet Status:
----------------------------------------
 1. 🟢 Living Room Lamp        [ON]
 2. 🔴 Bedroom Fan             [OFF]
 3. 🟢 Kitchen Appliance       [ON]
 4. 🔴 Office Computer         [OFF]
 5. 🔴 Gaming Setup            [OFF]
 6. 🟢 Home Theater            [ON]

Options:
1-6. Select outlet to control
  r. Refresh status
  q. Quit
----------------------------------------
```

### Outlet Control Menu

When you select an outlet, you'll see a control menu:

```
==================================================
Controlling: 🟢 Living Room Lamp
Current Status: ON
==================================================

Options:
  on.  Turn outlet ON
  off. Turn outlet OFF
  b.   Back to main menu
------------------------------
```

### Commands

- **1-6**: Select outlet to control
- **r**: Refresh outlet status
- **q**: Quit the application
- **on**: Turn selected outlet ON
- **off**: Turn selected outlet OFF
- **b**: Back to main menu
- **Ctrl+C**: Exit the application

## Finding Your Power Strip IP

### Method 1: Router Admin Interface
1. Log into your router's admin interface
2. Look for "Connected Devices" or "DHCP Client List"
3. Find your TP-Link power strip in the list ( it should be hs300 )

### Method 2: Network Scanner
Use a network scanner like `nmap`:
```bash
nmap -sn 192.168.1.0/24
```

### Method 3: Kasa App
1. Open the Kasa app
2. Find your power strip in the device list
3. Check the device details for the IP address

## Troubleshooting

### Connection Issues

1. **"Connection failed" error**:
   - Verify the IP address is correct
   - Ensure the power strip is powered on
   - Check network connectivity
   - Try pinging the IP address: `ping 192.168.2.3`

2. **"Error getting system info"**:
   - The power strip might be busy
   - Try refreshing the status
   - Restart the power strip if necessary

### Common Issues

1. **Wrong IP address**: Double-check the IP address in your network
2. **Network connectivity**: Ensure your computer and power strip are on the same network
3. **Power strip not responding**: Try power cycling the power strip
4. **Permission issues**: Run with appropriate permissions if needed

## Development

### Project Structure

```
Python-KasaSmartPowerStrip/
├── src/
│   ├── __init__.py
│   └── kasa_cli.py          # Main CLI application
├── tests/
│   ├── __init__.py
│   └── test_kasa_cli.py     # Unit tests
├── KasaSmartPowerStrip.py   # Enhanced library
├── config.py                # Configuration file
├── setup.py                 # Package setup
├── pyproject.toml          # Project configuration
├── requirements.txt         # Dependencies
└── README.md               # This file
```

### Running Tests

#### Using `uv` (Recommended)

```bash
# Install test dependencies (minimal set)
uv add --dev pytest pytest-cov pytest-mock

# Or install from requirements-test.txt
uv pip install -r requirements-test.txt

# Run all tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_kasa_cli.py -v

# Run specific test method
uv run pytest tests/test_kasa_cli.py::TestKasaPowerStripCLI::test_init -v
```

#### Using `pytest` directly

```bash
# Install pytest if not already installed
pip install -r requirements-test.txt

# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html
```

#### Using `unittest`

```bash
# Run tests with unittest (no additional dependencies needed)
python -m unittest discover -s tests -v
```

#### Using the test runner script

```bash
# Run tests with automatic runner detection
python run_tests.py
```

### Test Configuration

The project includes a `pyproject.toml` file with test configuration:

- **Test paths**: `tests/`
- **Test patterns**: `test_*.py`, `Test*` classes, `test_*` functions
- **Coverage**: Configured to cover `src/` directory

### Code Style

This project follows PEP 8 style guidelines. Use a linter like `flake8`:

```bash
# Install development dependencies (optional)
uv add --dev black flake8 mypy

# Format code with black
uv run black src/ tests/

# Check code style with flake8
uv run flake8 src/ tests/

# Type checking with mypy
uv run mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original KasaSmartPowerStrip library by p-doyle
- TP-Link for the HS300 Smart Power Strip

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the original KasaSmartPowerStrip library documentation
3. Open an issue on the project repository


## To get IP address of HS300 on PEPWAVE
ssh admin@192.168.50.1 -p 8822
get clientlist
