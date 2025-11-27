#!/usr/bin/env python3
"""
Simple script to run the Flask web application.

Usage:
    python run_web_app.py [--port PORT] [--debug]
"""

import argparse
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import app, power_strip_ip

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run TP-Link HS300 Web Controller')
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.environ.get('PORT', 5000)),
        help='Port number (default: 5000)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        help='Enable debug mode'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("TP-Link HS300 Power Strip Web Controller")
    print("=" * 60)
    print(f"Power Strip IP: {power_strip_ip}")
    print(f"Server URL: http://localhost:{args.port}")
    print(f"Debug Mode: {args.debug}")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host=args.host, port=args.port, debug=args.debug)

