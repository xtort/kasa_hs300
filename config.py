#!/usr/bin/env python3
"""
Configuration file for the TP-Link HS300 Power Strip CLI.

This file contains configuration settings that can be easily modified
without changing the main application code.
"""

# Power Strip Configuration
POWER_STRIP_IP = "192.168.2.3"
POWER_STRIP_TIMEOUT = 2.0
POWER_STRIP_PROTOCOL = "tcp"  # 'tcp' or 'udp'

# CLI Configuration
CLI_REFRESH_DELAY = 1.0  # seconds
CLI_SHOW_EMOJIS = True   # Enable/disable emoji indicators

# Outlet Configuration
MAX_OUTLETS = 6  # Maximum number of outlets on HS300
# Outlet names are pulled directly from the power strip, set them using the mobile Kasa app
DEFAULT_OUTLET_NAMES = {
    1: "Outlet 1",
    2: "Outlet 2", 
    3: "Outlet 3",
    4: "Outlet 4",
    5: "Outlet 5",
    6: "Outlet 6"
}
