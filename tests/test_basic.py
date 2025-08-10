#!/usr/bin/env python3
"""
Basic tests to verify the testing setup works correctly.
"""

import unittest
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBasicSetup(unittest.TestCase):
    """Basic tests to verify the testing setup works."""

    def test_import_kasa_cli(self):
        """Test that the kasa_cli module can be imported."""
        try:
            from src.kasa_cli import KasaPowerStripCLI
            self.assertTrue(True, "Successfully imported KasaPowerStripCLI")
        except ImportError as e:
            self.fail(f"Failed to import KasaPowerStripCLI: {e}")

    def test_import_kasa_smart_power_strip(self):
        """Test that the KasaSmartPowerStrip module can be imported."""
        try:
            from KasaSmartPowerStrip import SmartPowerStrip
            self.assertTrue(True, "Successfully imported SmartPowerStrip")
        except ImportError as e:
            self.fail(f"Failed to import SmartPowerStrip: {e}")

    def test_cli_initialization(self):
        """Test that the CLI can be initialized."""
        try:
            from src.kasa_cli import KasaPowerStripCLI
            cli = KasaPowerStripCLI("192.168.2.3")
            self.assertEqual(cli.ip_address, "192.168.2.3")
            self.assertIsNone(cli.power_strip)
            self.assertEqual(cli.outlet_names, {})
            self.assertEqual(cli.outlet_states, {})
        except Exception as e:
            self.fail(f"Failed to initialize CLI: {e}")

    def test_basic_math(self):
        """A simple test to verify the testing framework works."""
        self.assertEqual(2 + 2, 4)
        self.assertNotEqual(2 + 2, 5)


if __name__ == "__main__":
    unittest.main()
