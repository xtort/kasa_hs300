#!/usr/bin/env python3
"""
Demo script for the TP-Link HS300 Power Strip CLI.

This script demonstrates how to use the CLI application programmatically.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.kasa_cli import KasaPowerStripCLI


def demo_basic_usage():
    """Demonstrate basic usage of the CLI."""
    print("=== TP-Link HS300 Power Strip CLI Demo ===\n")
    
    # Create CLI instance
    cli = KasaPowerStripCLI("192.168.2.3")
    
    # Try to connect
    if not cli.connect():
        print("Failed to connect to power strip. Please check:")
        print("1. Power strip is powered on")
        print("2. IP address is correct")
        print("3. Network connectivity")
        return
    
    print("✓ Successfully connected to power strip!")
    
    # Get system info
    sys_info = cli.get_system_info()
    if sys_info:
        device_name = sys_info['system']['get_sysinfo']['alias']
        print(f"Device Name: {device_name}")
    
    # Update outlet info
    if cli.update_outlet_info():
        print(f"Found {len(cli.outlet_states)} outlets")
        
        # Display outlet status
        print("\nOutlet Status:")
        for outlet_num in sorted(cli.outlet_states.keys()):
            state = "ON" if cli.outlet_states[outlet_num] == 1 else "OFF"
            name = cli.outlet_names[outlet_num]
            status_indicator = "🟢" if state == "ON" else "🔴"
            print(f"  {outlet_num}. {status_indicator} {name:<20} [{state}]")
    
    print("\nTo run the full interactive CLI, use:")
    print("  python src/kasa_cli.py --ip 192.168.2.3")
    print("  or")
    print("  python run_cli.py")


def demo_programmatic_control():
    """Demonstrate programmatic control of outlets."""
    print("\n=== Programmatic Control Demo ===\n")
    
    cli = KasaPowerStripCLI("192.168.2.3")
    
    if not cli.connect():
        print("Failed to connect. Skipping programmatic demo.")
        return
    
    # Update outlet info
    if not cli.update_outlet_info():
        print("Failed to get outlet info. Skipping programmatic demo.")
        return
    
    # Demonstrate controlling outlets programmatically
    print("Demonstrating programmatic outlet control...")
    
    # Turn on outlet 1
    print("Turning ON outlet 1...")
    if cli.control_outlet(1, "on"):
        print("✓ Successfully turned ON outlet 1")
    else:
        print("✗ Failed to turn ON outlet 1")
    
    # Wait a moment
    import time
    time.sleep(2)
    
    # Turn off outlet 1
    print("Turning OFF outlet 1...")
    if cli.control_outlet(1, "off"):
        print("✓ Successfully turned OFF outlet 1")
    else:
        print("✗ Failed to turn OFF outlet 1")


if __name__ == "__main__":
    print("TP-Link HS300 Power Strip CLI Demo")
    print("=" * 40)
    
    try:
        demo_basic_usage()
        demo_programmatic_control()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
    
    print("\nDemo completed!")
