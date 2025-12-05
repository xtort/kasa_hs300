#!/usr/bin/env python3
"""
Debug script to examine the actual device information and plug IDs.
This will help us understand why the toggle_plugs isn't working.
"""

import sys
import os
import json

# Add the parent directory to the path to import KasaSmartPowerStrip
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from KasaSmartPowerStrip import SmartPowerStrip
except ImportError as e:
    print(f"Error importing KasaSmartPowerStrip: {e}")
    print("Make sure KasaSmartPowerStrip.py is in the same directory.")
    sys.exit(1)
if len(sys.argv) > 1:
    ip = sys.argv[1]
else:
    ip = "192.168.2.57"

def debug_device_info(ip):
    """Debug the device information and plug ID generation."""
    
    # IP address of your power strip (change this to match your setup)
    #ip_address = "192.168.2.3"  # Update this to your power strip's IP
    ip_address = ip
    
    print("Debugging device information and plug ID generation...")
    print(f"Power strip IP: {ip_address}")
    print("=" * 70)
    
    try:
        # Connect to the power strip
        print("Connecting to power strip...")
        power_strip = SmartPowerStrip(ip_address)
        print("✓ Connected successfully!")
        
        # Get system info
        print("\n1. SYSTEM INFO:")
        print("-" * 30)
        sys_info = power_strip.get_system_info()
        print(f"Device ID: {power_strip.device_id}")
        print(f"System info keys: {list(sys_info.keys())}")
        
        if 'system' in sys_info and 'get_sysinfo' in sys_info['system']:
            sys_details = sys_info['system']['get_sysinfo']
            print(f"System details keys: {list(sys_details.keys())}")
            
            if 'children' in sys_details:
                print(f"\n2. PLUG CHILDREN INFO:")
                print("-" * 30)
                children = sys_details['children']
                print(f"Number of children: {len(children)}")
                
                for i, child in enumerate(children):
                    print(f"\nChild {i+1}:")
                    print(f"  Keys: {list(child.keys())}")
                    print(f"  ID: {child.get('id', 'N/A')}")
                    print(f"  Alias: {child.get('alias', 'N/A')}")
                    print(f"  State: {child.get('state', 'N/A')}")
                    print(f"  On time: {child.get('on_time', 'N/A')}")
        
        # Test plug ID generation
        print(f"\n3. PLUG ID GENERATION TEST:")
        print("-" * 30)
        print(f"Device ID: {power_strip.device_id}")
        
        for plug_num in range(1, 7):
            try:
                plug_id = power_strip._get_plug_id(plug_num=plug_num)
                print(f"Plug {plug_num} → ID: {plug_id}")
            except Exception as e:
                print(f"Plug {plug_num} → Error: {e}")
        
        # Test the specific plug IDs you provided
        print(f"\n4. YOUR PROVIDED PLUG IDS:")
        print("-" * 30)
        your_plug_ids = [
            '8006C1B5C1BEB309F3DC5C15D3A2F79121B4900100',
            '8006C1B5C1BEB309F3DC5C15D3A2F79121B4900101',
            '8006C1B5C1BEB309F3DC5C15D3A2F79121B4900102',
            '8006C1B5C1BEB309F3DC5C15D3A2F79121B4900103',
            '8006C1B5C1BEB309F3DC5C15D3A2F79121B4900104',
            '8006C1B5C1BEB309F3DC5C15D3A2F79121B4900105'
        ]
        
        for i, plug_id in enumerate(your_plug_ids, 1):
            print(f"Your Plug {i} ID: {plug_id}")
        
        # Check if there's a pattern
        print(f"\n5. PATTERN ANALYSIS:")
        print("-" * 30)
        if power_strip.device_id:
            base_id = power_strip.device_id
            print(f"Base device ID: {base_id}")
            print(f"Base ID length: {len(base_id)}")
            
            for i, your_id in enumerate(your_plug_ids):
                if your_id.startswith(base_id):
                    suffix = your_id[len(base_id):]
                    print(f"Your Plug {i+1} suffix: '{suffix}' (length: {len(suffix)})")
                else:
                    print(f"Your Plug {i+1}: Does not start with base device ID")
        
        print("\n" + "=" * 70)
        print("Debug completed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"✗ Error during debugging: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("TP-Link HS300 Power Strip - Device Info Debug Script")
    print("This script will help us understand the plug ID mismatch")
    
    debug_device_info(ip)
    
    print("\nDebug script completed!")
