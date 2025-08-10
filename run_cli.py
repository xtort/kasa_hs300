#!/usr/bin/env python3
"""
Simple launcher script for the TP-Link HS300 Power Strip CLI.
"""

from src.kasa_cli import main
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    main()
