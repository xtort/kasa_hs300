# TP-Link HS300 Power Strip Web Controller
# VERSION 1.0a

A modern web-based interface for controlling TP-Link HS300 Smart Power Strip outlets. This Flask application provides all the capabilities of the CLI application in a user-friendly browser interface.

## Features

- **Dashboard View**: See all outlets at a glance with their current status (ON/OFF)
- **Individual Control**: Turn individual outlets on or off
- **Bulk Control**: Turn all outlets on or off with a single click
- **Power Monitoring**: View real-time power draw information (voltage, current, power, total energy) for each outlet
- **Auto-refresh**: Refresh outlet status with a single click
- **Modern UI**: Beautiful, responsive design that works on desktop and mobile devices

## Requirements

- Python 3.7 or higher
- Flask (see `requirements.txt`)
- Access to the TP-Link HS300 power strip on your network
- The `KasaSmartPowerStrip.py` library (should be in the parent directory)

## Installation

1. Install Flask and dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the power strip IP address is configured correctly:
   - The app uses the IP address from `config.py` in the parent directory
   - Default IP: `192.168.50.137`
   - You can modify this in `config.py` or set it as an environment variable

## Running the Application

### Basic Usage

```bash
cd web_app
python app.py
```

The application will start on `http://localhost:5000` by default.

### Configuration Options

You can configure the application using environment variables:

- `PORT`: Port number (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (default: False)

Example:
```bash
PORT=8080 FLASK_DEBUG=true python app.py
```

## Usage

1. **Access the Web Interface**: Open your browser and navigate to `http://localhost:5000`

2. **View Outlets**: The main dashboard shows all outlets with their current status

3. **Control Outlets**:
   - Click the **ON** or **OFF** button on any outlet card to toggle it
   - Use **Turn All On** or **Turn All Off** to control all outlets at once

4. **View Power Draw**:
   - Click the **Power** button on any outlet card
   - A modal will display real-time power information including:
     - Voltage (V)
     - Current (A)
     - Power (W)
     - Total Energy (kWh)

5. **Refresh Status**: Click the **Refresh** button to update all outlet statuses

## API Endpoints

The application provides RESTful API endpoints:

- `GET /api/outlets` - Get all outlet information
- `POST /api/outlet/<outlet_num>/toggle` - Toggle a specific outlet (body: `{"action": "on"|"off"|"toggle"}`)
- `POST /api/outlets/all` - Toggle all outlets (body: `{"action": "on"|"off"}`)
- `GET /api/outlet/<outlet_num>/power` - Get power draw information for an outlet

## Project Structure

```
web_app/
├── app.py              # Main Flask application
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── templates/          # HTML templates
│   ├── base.html       # Base template
│   └── index.html      # Main dashboard
└── static/            # Static files
    ├── css/
    │   └── style.css   # Stylesheet
    └── js/
        └── main.js     # JavaScript functionality
```

## Troubleshooting

### Connection Issues

If you see "Failed to connect to power strip":
- Verify the power strip IP address in `config.py`
- Ensure the power strip is powered on and connected to your network
- Check that your computer can reach the power strip on the network

### Port Already in Use

If port 5000 is already in use:
```bash
PORT=8080 python app.py
```

### Module Import Errors

Ensure you're running the app from the `web_app` directory and that `KasaSmartPowerStrip.py` is in the parent directory.

## Security Note

This application is designed for local network use. For production deployment:
- Change the `SECRET_KEY` in `app.py`
- Consider adding authentication
- Use HTTPS if accessing over the internet
- Review Flask security best practices

## License

Same license as the parent project.

