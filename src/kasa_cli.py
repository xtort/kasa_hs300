#!/usr/bin/env python3
"""
CLI application for controlling TP-Link HS300 Smart Power Strip.

This module provides a command-line interface for managing individual outlets
on a TP-Link HS300 power strip, including viewing status and controlling
individual outlets. This allows for something like a remote rasberry pi that you can use to control the power strip.
"""

import sys
import os
import time
from typing import List, Dict, Optional, Tuple

# Add the parent directory to the path to import KasaSmartPowerStrip
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the SmartPowerStrip class
try:
    from KasaSmartPowerStrip import SmartPowerStrip
except ImportError as e:
    print(f"Error importing KasaSmartPowerStrip: {e}")
    print("Make sure KasaSmartPowerStrip.py is in the parent directory.")
    sys.exit(1)


class KasaPowerStripCLI:
    """CLI interface for controlling TP-Link HS300 Smart Power Strip."""

    def __init__(self, ip_address: str = "192.168.50.137"):
        """
        Initialize the CLI with the power strip IP address.

        Args:
            ip_address: IP address of the power strip
        """
        self.ip_address = ip_address
        self.power_strip = None
        self.selected_outlet = None
        self.outlet_names = {}
        self.outlet_states = {}

    def connect(self) -> bool:
        """
        Connect to the power strip.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            print(f"Connecting to power strip at {self.ip_address}...")
            self.power_strip = SmartPowerStrip(self.ip_address)
            print("✓ Connected successfully!")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    def get_system_info(self) -> Optional[Dict]:
        """
        Get system information from the power strip.

        Returns:
            System information dictionary or None if failed
        """
        try:
            return self.power_strip.get_system_info()
        except Exception as e:
            print(f"Error getting system info: {e}")
            return None

    def update_outlet_info(self) -> bool:
        """
        Update outlet information including names and states.

        Returns:
            True if successful, False otherwise
        """
        try:
            sys_info = self.get_system_info()
            if not sys_info:
                return False

            children = sys_info['system']['get_sysinfo']['children']

            for i, child in enumerate(children, 1):
                self.outlet_names[i] = child.get('alias', f'Outlet {i}')
                self.outlet_states[i] = child.get('state', 0)

            return True
        except Exception as e:
            print(f"Error updating outlet info: {e}")
            return False

    def clear_screen(self) -> None:
        """Clears the terminal screen based on the operating system."""
        if os.name == 'nt':  # For Windows
            os.system('cls')
        else:  # For Unix-like systems (Linux, macOS)
            os.system('clear')


    def display_main_menu(self) -> None:
        # self.clear_screen()
        """Display the main menu with all outlet statuses."""
        print("\n" + "="*60)
        print("           TP-Link HS300 Power Strip Controller")
        print("="*60)

        if not self.update_outlet_info():
            print("Failed to get outlet information.")
            return

        print(f"\nPower Strip IP: {self.ip_address}")
        print(
            f"Device Name: {self.get_system_info()['system']['get_sysinfo']['alias']}")
        print("\nOutlet Status:")
        print("-" * 40)

        for outlet_num in sorted(self.outlet_states.keys()):
            state = "ON" if self.outlet_states[outlet_num] == 1 else "OFF"
            name = self.outlet_names[outlet_num]
            status_indicator = "🟢" if state == "ON" else "🔴"
            print(f"{outlet_num:2d}. {status_indicator} {name:<20} [{state}]")

        print("\nOptions:")
        print("1-6. Select outlet to control")
        print("  o. Turn on all outlets")
        print("  f. Turn off all outlets")
        print("  r. Refresh status")
        print("  q. Quit")
        print("-" * 40)

    def display_outlet_menu(self, outlet_num: int) -> None:
        """
        Display menu for controlling a specific outlet.

        Args:
            outlet_num: The outlet number to control
        """
        if outlet_num not in self.outlet_states:
            print(f"Invalid outlet number: {outlet_num}")
            return

        self.selected_outlet = outlet_num
        outlet_name = self.outlet_names[outlet_num]
        current_state = "ON" if self.outlet_states[outlet_num] == 1 else "OFF"
        status_indicator = "🟢" if current_state == "ON" else "🔴"

        print(f"\n{'='*50}")
        print(f"Controlling: {status_indicator} {outlet_name}")
        print(f"Current Status: {current_state}")
        print(f"{'='*50}")

        print("\nOptions:")
        print("  on.  Turn outlet ON")
        print("  off. Turn outlet OFF")
        print("  p.   Show power draw")
        print("  b.   Back to main menu")
        print("-" * 30)

    def display_power_draw(self, outlet_num: int) -> bool:
        """
        Display power draw information for a specific outlet.

        Args:
            outlet_num: The outlet number to get power draw for

        Returns:
            True if successful, False otherwise
        """
        try:
            energy_info = self.power_strip.get_realtime_energy_info(plug_num=outlet_num)
            outlet_name = self.outlet_names[outlet_num]
            
            print(f"\n{'='*50}")
            print(f"Power Draw - {outlet_name} (Outlet {outlet_num})")
            print(f"{'='*50}")
            
            # Display power information
            # TP-Link Kasa devices typically return voltage, current, power, and total
            if 'voltage' in energy_info:
                print(f"Voltage:     {energy_info['voltage']:.2f} V")
            if 'current' in energy_info:
                print(f"Current:     {energy_info['current']:.3f} A")
            if 'power' in energy_info:
                print(f"Power:       {energy_info['power']:.2f} W")
            print(f"Total Energy: {energy_info['total']:.3f / 1000}  kWh")
            # if 'total' in energy_info:
            #     print(f"Total Energy: {energy_info['total']:.3f} kWh")
            
            # Some devices may use different field names
            if 'voltage_mv' in energy_info:
                print(f"Voltage:     {energy_info['voltage_mv'] / 1000:.2f} V")
            if 'current_ma' in energy_info:
                print(f"Current:     {energy_info['current_ma'] / 1000:.3f} A")
            if 'power_mw' in energy_info:
                print(f"Power:       {energy_info['power_mw'] / 1000:.2f} W")
            
            print(f"{'='*50}\n")
            return True
        except Exception as e:
            print(f"✗ Error getting power draw for outlet {outlet_num}: {e}")
            return False

    def control_outlet(self, outlet_num: int, action: str) -> bool:
        """
        Control a specific outlet.

        Args:
            outlet_num: The outlet number to control
            action: 'on' or 'off'

        Returns:
            True if successful, False otherwise
        """
        try:
            if action.lower() == 'on':
                result = self.power_strip.toggle_plug(
                    'on', plug_num=outlet_num)
                print(f"✓ Turned ON outlet {outlet_num}")
            elif action.lower() == 'off':
                result = self.power_strip.toggle_plug(
                    'off', plug_num=outlet_num)
                print(f"✓ Turned OFF outlet {outlet_num}")
            else:
                print(f"Invalid action: {action}")
                return False

            # Update the outlet state
            self.outlet_states[outlet_num] = 1 if action.lower() == 'on' else 0

            return True
        except Exception as e:
            print(f"✗ Error controlling outlet {outlet_num}: {e}")
            return False

    def toggle_all_outlets(self, action: str) -> bool:
        """
        Toggle all outlets.

        Args:
            action: 'on' or 'off'

        Returns:
            True if successful, False otherwise
        """
        plug_num_list = list(self.outlet_states.keys())
        print("A list of all the outlet numbers:")
        print(
            f"list(self.outlet_states.keys()): {list(self.outlet_states.keys())}")
        print(plug_num_list)
        try:
            return self.power_strip.toggle_plugs(action, plug_num_list=plug_num_list)
        except Exception as e:
            print(f"✗ Error toggling all outlets: {e}")
            return False

    def run(self) -> None:
        """Run the main CLI loop."""
        if not self.connect():
            return

        while True:
            try:
                self.display_main_menu()
                choice = input("\nEnter your choice: ").strip().lower()

                if choice == 'q':
                    print("Goodbye!")
                    break
                elif choice == 'r':
                    print("Refreshing status...")
                    time.sleep(1)
                    continue
                elif choice.isdigit():
                    outlet_num = int(choice)
                    if outlet_num in self.outlet_states:
                        self.run_outlet_control_loop(outlet_num)
                    else:
                        print(f"Invalid outlet number: {outlet_num}")
                elif choice == 'o':
                    self.toggle_all_outlets('on')
                elif choice == 'f':
                    self.toggle_all_outlets('off')
                else:
                    print("Invalid choice. Please try again.")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")

    def run_outlet_control_loop(self, outlet_num: int) -> None:
        """
        Run the outlet control loop for a specific outlet.

        Args:
            outlet_num: The outlet number to control
        """
        while True:
            try:
                self.display_outlet_menu(outlet_num)
                choice = input("Enter your choice: ").strip().lower()

                if choice == 'b':
                    break
                elif choice in ['on', 'off']:
                    if self.control_outlet(outlet_num, choice):
                        time.sleep(1)  # Brief pause to show the action
                    else:
                        print("Failed to control outlet.")
                elif choice == 'p':
                    self.display_power_draw(outlet_num)
                    input("\nPress Enter to continue...")
                else:
                    print("Invalid choice. Please try again.")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error in outlet control: {e}")


def main():
    """Main entry point for the CLI application."""
    import argparse

    parser = argparse.ArgumentParser(
        description="CLI for controlling TP-Link HS300 Smart Power Strip"
    )
    parser.add_argument(
        "--ip",
        default="192.168.50.137",
        help="IP address of the power strip (default: 192.168.2.3)"
    )

    args = parser.parse_args()

    cli = KasaPowerStripCLI(args.ip)
    cli.run()


if __name__ == "__main__":
    main()
