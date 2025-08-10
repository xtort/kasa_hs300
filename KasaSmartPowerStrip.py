#!/usr/bin/env python3
"""
TP-Link Kasa Smart Power Strip library.

"""

import socket
import json
import struct
import time
from typing import Optional, List, Dict, Union, Any
from builtins import bytes


class SmartPowerStrip:

    def __init__(self, ip: str, device_id: Optional[str] = None,
                 timeout: float = 2.0, protocol: str = 'tcp'):
        """
        Initialize the power strip controller.

        Args:
            ip: IP address of the power strip
            device_id: Device ID (auto-detected if not provided)
            timeout: Connection timeout in seconds
            protocol: Communication protocol ('tcp' or 'udp')

        Raises:
            ConnectionError: If unable to connect to the power strip
            ValueError: If invalid parameters are provided
        """
        if not ip:
            raise ValueError("IP address is required")

        if protocol not in ['tcp', 'udp']:
            raise ValueError("Protocol must be 'tcp' or 'udp'")

        self.ip = ip
        self.port = 9999
        self.protocol = protocol
        self.device_id = device_id
        self.timeout = timeout
        self.sys_info = None

        # Initialize connection and get system info
        try:
            self.sys_info = self.get_system_info()['system']['get_sysinfo']
            if not self.device_id:
                self.device_id = self.sys_info['deviceId']
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to power strip at {ip}: {e}")

    def set_wifi_credentials(self, ssid: str, psk: str, key_type: str = '3') -> Dict[str, Any]:
        """
        Set WiFi credentials for the power strip.

        Args:
            ssid: Router SSID
            psk: Router passkey
            key_type: Key type ('3' for WPA2, '2' for WPA, '1' for WEP)

        Returns:
            Command response from the power strip
        """
        wifi_command = (
            '{"netif":{"set_stainfo":{"ssid":"' + ssid +
            '","password":"' + psk + '","key_type":' + key_type + '}}}'
        )
        return self.send_command(wifi_command, self.protocol)

    def set_cloud_server_url(self, server_url: str = '') -> Dict[str, Any]:
        """
        Set the cloud server URL.

        Args:
            server_url: Cloud server URL (empty string to disable)

        Returns:
            Command response from the power strip
        """
        server_command = (
            '{"cnCloud":{"set_server_url":{"server":"' + server_url + '"}}}'
        )
        return self.send_command(server_command, self.protocol)

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information from the power strip.

        Returns:
            System information dictionary

        Raises:
            ConnectionError: If unable to communicate with the power strip
        """
        try:
            return self._udp_send_command('{"system":{"get_sysinfo":{}}}')
        except Exception as e:
            # Fallback to TCP if UDP fails
            try:
                return self._tcp_send_command('{"system":{"get_sysinfo":{}}}')
            except Exception as tcp_error:
                raise ConnectionError(
                    f"Failed to get system info: {e}, TCP fallback failed: {tcp_error}")

    def get_realtime_energy_info(self, plug_num: Optional[int] = None,
                                 plug_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get real-time energy information for a specific plug.

        Args:
            plug_num: Plug number (1-6)
            plug_name: Plug name (alternative to plug_num)

        Returns:
            Real-time energy data

        Raises:
            ValueError: If neither plug_num nor plug_name is provided
        """
        plug_id = self._get_plug_id(plug_num=plug_num, plug_name=plug_name)
        energy_command = (
            '{"context":{"child_ids":["' + plug_id + '"]},'
            '"emeter":{"get_realtime":{}}}'
        )
        response = self.send_command(energy_command, self.protocol)
        return response['emeter']['get_realtime']

    def get_historical_energy_info(self, month: Union[int, str], year: Union[int, str],
                                   plug_num: Optional[int] = None,
                                   plug_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get historical energy information for a specific plug.

        Args:
            month: Month (1-12)
            year: Year (e.g., 2023)
            plug_num: Plug number (1-6)
            plug_name: Plug name (alternative to plug_num)

        Returns:
            Historical energy data list
        """
        plug_id = self._get_plug_id(plug_num=plug_num, plug_name=plug_name)
        energy_command = (
            '{"context":{"child_ids":["' + plug_id + '"]},'
            '"emeter":{"get_daystat":{"month": ' + str(month) +
            ',"year":' + str(year) + '}}}'
        )
        response = self.send_command(energy_command, self.protocol)
        return response['emeter']['get_daystat']['day_list']

    def toggle_relay_leds(self, state: str) -> Dict[str, Any]:
        """
        Toggle relay LEDs on/off.

        Args:
            state: 'on' or 'off'

        Returns:
            Command response from the power strip
        """
        state_int = self._get_plug_state_int(state, reverse=True)
        led_command = '{"system":{"set_led_off":{"off":' + \
            str(state_int) + '}}}'
        return self.send_command(led_command, self.protocol)

    def set_plug_name(self, plug_num: int, plug_name: str) -> Dict[str, Any]:
        """
        Set the name of a specific plug.

        Args:
            plug_num: Plug number (1-6)
            plug_name: New name for the plug

        Returns:
            Command response from the power strip
        """
        plug_id = self._get_plug_id(plug_num=plug_num)
        set_name_command = (
            '{"context":{"child_ids":["' + plug_id + '"]},'
            '"system":{"set_dev_alias":{"alias":"' + plug_name + '"}}}'
        )
        return self.send_command(set_name_command, self.protocol)

    def get_plug_info(self, plug_num: int) -> List[Dict[str, Any]]:
        """
        Get information about a specific plug.

        Args:
            plug_num: Plug number (1-6)

        Returns:
            Plug information list
        """
        target_plug = [
            plug for plug in self.sys_info['children']
            if plug['id'] == str(int(plug_num) - 1).zfill(2)
        ]
        return target_plug

    def toggle_plugs(self, state: str, plug_num_list: Optional[List[int]] = None,
                     plug_name_list: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Toggle multiple plugs simultaneously.

        Args:
            state: 'on' or 'off'
            plug_num_list: List of plug numbers
            plug_name_list: List of plug names

        Returns:
            Command response from the power strip
        """
        state_int = self._get_plug_state_int(state)
        plug_id_list = self._get_plug_id_list(
            plug_num_list=plug_num_list, plug_name_list=plug_name_list
        )
        print(f"plug_id_list: {plug_id_list}")
        # Construct the JSON command properly using a dictionary and json.dumps
        all_relay_command = {
            "context": {"child_ids": plug_id_list},
            "system": {"set_relay_state": {"state": state_int}}
        }
        return self.send_command(json.dumps(all_relay_command), self.protocol)

    def toggle_plug(self, state: str, plug_num: Optional[int] = None,
                    plug_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Toggle a single plug.

        Args:
            state: 'on' or 'off'
            plug_num: Plug number (1-6)
            plug_name: Plug name (alternative to plug_num)

        Returns:
            Command response from the power strip
        """
        state_int = self._get_plug_state_int(state)
        plug_id = self._get_plug_id(plug_num=plug_num, plug_name=plug_name)
        relay_command = (
            '{"context":{"child_ids":["' + plug_id + '"]},'
            '"system":{"set_relay_state":{"state":' + str(state_int) + '}}}'
        )
        return self.send_command(relay_command, self.protocol)

    def reboot(self, delay: int = 1) -> Dict[str, Any]:
        """
        Reboot the power strip.

        Args:
            delay: Delay before reboot in seconds

        Returns:
            Command response from the power strip
        """
        reboot_command = '{"system":{"reboot":{"delay":' + str(delay) + '}}}'
        return self.send_command(reboot_command, self.protocol)

    def send_command(self, command: str, protocol: str = 'tcp') -> Dict[str, Any]:
        """
        Send a command to the power strip.

        Args:
            command: JSON command string
            protocol: Communication protocol ('tcp' or 'udp')

        Returns:
            Response from the power strip

        Raises:
            ValueError: If invalid protocol is specified
        """
        if protocol == 'tcp':
            return self._tcp_send_command(command)
        elif protocol == 'udp':
            return self._udp_send_command(command)
        else:
            raise ValueError("Protocol must be 'tcp' or 'udp'")

    def _get_plug_state_int(self, state: str, reverse: bool = False) -> int:
        """
        Convert state string to integer.

        Args:
            state: State string ('on' or 'off')
            reverse: Whether to reverse the logic

        Returns:
            State integer (0 or 1)

        Raises:
            ValueError: If invalid state is provided
        """
        state_lower = state.lower()
        if state_lower == 'on':
            return 0 if reverse else 1
        elif state_lower == 'off':
            return 1 if reverse else 0
        else:
            raise ValueError("Invalid state, must be 'on' or 'off'")

    def _get_plug_id_list(self, plug_num_list: Optional[List[int]] = None,
                          plug_name_list: Optional[List[str]] = None) -> List[str]:
        """
        Create a list of plug IDs.

        Args:
            plug_num_list: List of plug numbers
            plug_name_list: List of plug names

        Returns:
            List of plug ID strings
        """
        plug_id_list = []

        if plug_num_list:
            for plug_num in plug_num_list:
                plug_id_list.append(str(self._get_plug_id(plug_num=plug_num)))
        elif plug_name_list:
            for plug_name in plug_name_list:
                plug_id_list.append(
                    str(self._get_plug_id(plug_name=plug_name)))

        return plug_id_list

    def _get_plug_id_list_str(self, plug_num_list: Optional[List[int]] = None,
                              plug_name_list: Optional[List[str]] = None) -> str:
        """
        Create a string with a list of plug IDs.

        Args:
            plug_num_list: List of plug numbers
            plug_name_list: List of plug names

        Returns:
            JSON string of plug IDs
        """
        plug_id_list = self._get_plug_id_list(plug_num_list, plug_name_list)
        # Convert to double quotes and turn the whole list into a string
        return str(plug_id_list).replace("'", '"')

    def _get_plug_id(self, plug_num: Optional[int] = None,
                     plug_name: Optional[str] = None) -> str:
        """
        Get the plug child ID for commands.

        Args:
            plug_num: Plug number (1-6)
            plug_name: Plug name (alternative to plug_num)

        Returns:
            Plug ID string

        Raises:
            ValueError: If unable to find plug or invalid parameters
        """
        if plug_num and self.device_id:
            plug_id = self.device_id + str(plug_num - 1).zfill(2)
        elif plug_name and self.sys_info:
            target_plug = [
                plug for plug in self.sys_info['children']
                if plug['alias'] == plug_name
            ]
            if target_plug:
                plug_id = self.device_id + target_plug[0]['id']
            else:
                raise ValueError(f'Unable to find plug with name {plug_name}')
        else:
            raise ValueError(
                'Unable to find plug. Provide a valid plug_num or plug_name')

        return plug_id

    def _tcp_send_command(self, command: str) -> Dict[str, Any]:
        """
        Send command via TCP.

        Args:
            command: JSON command string

        Returns:
            Response from the power strip
        """
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.settimeout(self.timeout)

        try:
            sock_tcp.connect((self.ip, self.port))
            sock_tcp.send(self._encrypt_command(command))
            data = sock_tcp.recv(2048)
            # The first 4 chars are the length of the command so can be excluded
            return json.loads(self._decrypt_command(data[4:]))
        finally:
            sock_tcp.close()

    def _udp_send_command(self, command: str) -> Dict[str, Any]:
        """
        Send command via UDP.

        Args:
            command: JSON command string

        Returns:
            Response from the power strip
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(self.timeout)

        try:
            addr = (self.ip, self.port)
            client_socket.sendto(
                self._encrypt_command(command, prepend_length=False), addr
            )
            data, server = client_socket.recvfrom(2048)
            return json.loads(self._decrypt_command(data))
        finally:
            client_socket.close()

    @staticmethod
    def _encrypt_command(string: str, prepend_length: bool = True) -> bytes:
        """
        Encrypt command for transmission.

        Args:
            string: Command string to encrypt
            prepend_length: Whether to prepend length

        Returns:
            Encrypted command bytes
        """
        key = 171
        result = b''

        # When sending get_sysinfo using UDP the length is not needed
        # but with all other commands using TCP it is
        if prepend_length:
            result = struct.pack(">I", len(string))

        for i in bytes(string.encode('latin-1')):
            a = key ^ i
            key = a
            result += bytes([a])
        return result

    @staticmethod
    def _decrypt_command(string: bytes) -> str:
        """
        Decrypt response from power strip.

        Args:
            string: Encrypted response bytes

        Returns:
            Decrypted response string
        """
        key = 171
        result = b''
        for i in bytes(string):
            a = key ^ i
            key = i
            result += bytes([a])
        return result.decode('latin-1')

    def get_all_plugs_status(self) -> Dict[int, Dict[str, Any]]:
        """
        Get status of all plugs.

        Returns:
            Dictionary mapping plug numbers to their status information
        """
        status = {}
        for i in range(1, len(self.sys_info['children']) + 1):
            plug_info = self.get_plug_info(i)
            if plug_info:
                status[i] = {
                    'name': plug_info[0].get('alias', f'Outlet {i}'),
                    'state': plug_info[0].get('state', 0),
                    'id': plug_info[0].get('id', ''),
                    'on_time': plug_info[0].get('on_time', 0)
                }
        return status

    def turn_all_plugs(self, state: str) -> Dict[str, Any]:
        """
        Turn all plugs on or off.

        Args:
            state: 'on' or 'off'

        Returns:
            Command response from the power strip
        """
        plug_numbers = list(range(1, len(self.sys_info['children']) + 1))
        return self.toggle_plugs(state, plug_num_list=plug_numbers)

    def get_plug_count(self) -> int:
        """
        Get the number of plugs on the power strip.

        Returns:
            Number of plugs
        """
        return len(self.sys_info['children']) if self.sys_info else 0

    def is_plug_on(self, plug_num: Optional[int] = None, plug_name: Optional[str] = None) -> bool:
        """
        Check if a specific plug is on.

        Args:
            plug_num: Plug number (1-6)
            plug_name: Plug name (alternative to plug_num)

        Returns:
            True if plug is on, False otherwise
        """
        if plug_num:
            plug_info = self.get_plug_info(plug_num)
            if plug_info:
                return plug_info[0].get('state', 0) == 1
        elif plug_name:
            for plug in self.sys_info['children']:
                if plug.get('alias') == plug_name:
                    return plug.get('state', 0) == 1
        return False
