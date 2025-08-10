#!/usr/bin/env python3
"""
Tests for the KasaPowerStripCLI class.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path to import the CLI module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.kasa_cli import KasaPowerStripCLI


class TestKasaPowerStripCLI(unittest.TestCase):
    """Test cases for KasaPowerStripCLI class."""

    def setUp(self):
        """Set up test fixtures."""
        self.cli = KasaPowerStripCLI("192.168.2.3")

    def test_init(self):
        """Test CLI initialization."""
        self.assertEqual(self.cli.ip_address, "192.168.2.3")
        self.assertIsNone(self.cli.power_strip)
        self.assertIsNone(self.cli.selected_outlet)
        self.assertEqual(self.cli.outlet_names, {})
        self.assertEqual(self.cli.outlet_states, {})

    def test_connect_success(self):
        """Test successful connection."""
        with patch('src.kasa_cli.SmartPowerStrip') as mock_smart_strip:
            mock_instance = Mock()
            mock_smart_strip.return_value = mock_instance
            
            result = self.cli.connect()
            
            self.assertTrue(result)
            self.assertEqual(self.cli.power_strip, mock_instance)
            mock_smart_strip.assert_called_once_with("192.168.2.3")

    def test_connect_failure(self):
        """Test connection failure."""
        with patch('src.kasa_cli.SmartPowerStrip') as mock_smart_strip:
            mock_smart_strip.side_effect = Exception("Connection failed")
            
            result = self.cli.connect()
            
            self.assertFalse(result)
            self.assertIsNone(self.cli.power_strip)

    def test_get_system_info_success(self):
        """Test successful system info retrieval."""
        mock_sys_info = {"system": {"get_sysinfo": {"alias": "Test Strip"}}}
        self.cli.power_strip = Mock()
        self.cli.power_strip.get_system_info.return_value = mock_sys_info
        
        result = self.cli.get_system_info()
        
        self.assertEqual(result, mock_sys_info)
        self.cli.power_strip.get_system_info.assert_called_once()

    def test_get_system_info_failure(self):
        """Test system info retrieval failure."""
        self.cli.power_strip = Mock()
        self.cli.power_strip.get_system_info.side_effect = Exception("Network error")
        
        result = self.cli.get_system_info()
        
        self.assertIsNone(result)

    def test_update_outlet_info_success(self):
        """Test successful outlet info update."""
        mock_sys_info = {
            "system": {
                "get_sysinfo": {
                    "children": [
                        {"alias": "Outlet 1", "state": 1, "id": "00"},
                        {"alias": "Outlet 2", "state": 0, "id": "01"}
                    ]
                }
            }
        }
        
        with patch.object(self.cli, 'get_system_info', return_value=mock_sys_info):
            result = self.cli.update_outlet_info()
            
            self.assertTrue(result)
            self.assertEqual(self.cli.outlet_names[1], "Outlet 1")
            self.assertEqual(self.cli.outlet_names[2], "Outlet 2")
            self.assertEqual(self.cli.outlet_states[1], 1)
            self.assertEqual(self.cli.outlet_states[2], 0)

    def test_update_outlet_info_failure(self):
        """Test outlet info update failure."""
        with patch.object(self.cli, 'get_system_info', return_value=None):
            result = self.cli.update_outlet_info()
            
            self.assertFalse(result)

    def test_control_outlet_on(self):
        """Test turning outlet on."""
        self.cli.power_strip = Mock()
        self.cli.power_strip.toggle_plug.return_value = {"error_code": 0}
        
        result = self.cli.control_outlet(1, "on")
        
        self.assertTrue(result)
        self.cli.power_strip.toggle_plug.assert_called_once_with('on', plug_num=1)
        self.assertEqual(self.cli.outlet_states[1], 1)

    def test_control_outlet_off(self):
        """Test turning outlet off."""
        self.cli.power_strip = Mock()
        self.cli.power_strip.toggle_plug.return_value = {"error_code": 0}
        
        result = self.cli.control_outlet(1, "off")
        
        self.assertTrue(result)
        self.cli.power_strip.toggle_plug.assert_called_once_with('off', plug_num=1)
        self.assertEqual(self.cli.outlet_states[1], 0)

    def test_control_outlet_invalid_action(self):
        """Test invalid action for outlet control."""
        result = self.cli.control_outlet(1, "invalid")
        
        self.assertFalse(result)

    def test_control_outlet_exception(self):
        """Test outlet control with exception."""
        self.cli.power_strip = Mock()
        self.cli.power_strip.toggle_plug.side_effect = Exception("Network error")
        
        result = self.cli.control_outlet(1, "on")
        
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
