#!/usr/bin/env python3
"""
Flask web application for controlling TP-Link HS300 Smart Power Strip.

This web application provides a browser-based interface for managing individual
outlets on a TP-Link HS300 power strip, including viewing status, controlling
outlets, and monitoring power draw.
"""

import sys
import os
from flask import Flask, render_template, jsonify, request
from typing import Dict, Optional

# Add the parent directory to the path to import KasaSmartPowerStrip
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from KasaSmartPowerStrip import SmartPowerStrip
    import config
except ImportError as e:
    print(f"Error importing dependencies: {e}")
    print("Make sure KasaSmartPowerStrip.py and config.py are in the parent directory.")
    sys.exit(1)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Global power strip instance
power_strip: Optional[SmartPowerStrip] = None
power_strip_ip = getattr(config, 'POWER_STRIP_IP', '192.168.50.137')


def get_power_strip() -> Optional[SmartPowerStrip]:
    """Get or create power strip connection."""
    global power_strip
    if power_strip is None:
        try:
            power_strip = SmartPowerStrip(power_strip_ip)
        except Exception as e:
            print(f"Failed to connect to power strip: {e}")
            return None
    return power_strip


def get_outlet_info() -> Dict:
    """Get outlet information from the power strip."""
    strip = get_power_strip()
    if not strip:
        return {'error': 'Failed to connect to power strip'}
    
    try:
        sys_info = strip.get_system_info()
        if not sys_info:
            return {'error': 'Failed to get system info'}
        
        children = sys_info['system']['get_sysinfo']['children']
        outlets = {}
        
        for i, child in enumerate(children, 1):
            outlets[i] = {
                'name': child.get('alias', f'Outlet {i}'),
                'state': child.get('state', 0),
                'id': child.get('id', ''),
                'on_time': child.get('on_time', 0)
            }
        
        device_name = sys_info['system']['get_sysinfo'].get('alias', 'HS300 Power Strip')
        
        return {
            'outlets': outlets,
            'device_name': device_name,
            'ip_address': power_strip_ip
        }
    except Exception as e:
        return {'error': str(e)}


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/api/outlets', methods=['GET'])
def get_outlets():
    """API endpoint to get all outlet information."""
    info = get_outlet_info()
    return jsonify(info)


@app.route('/api/outlet/<int:outlet_num>/toggle', methods=['POST'])
def toggle_outlet(outlet_num):
    """API endpoint to toggle a specific outlet."""
    strip = get_power_strip()
    if not strip:
        return jsonify({'success': False, 'error': 'Failed to connect to power strip'}), 500
    
    try:
        data = request.get_json()
        action = data.get('action', 'toggle')  # 'on', 'off', or 'toggle'
        
        # Get current state
        info = get_outlet_info()
        if 'error' in info:
            return jsonify({'success': False, 'error': info['error']}), 500
        
        if outlet_num not in info['outlets']:
            return jsonify({'success': False, 'error': f'Invalid outlet number: {outlet_num}'}), 400
        
        current_state = info['outlets'][outlet_num]['state']
        
        # Determine action
        if action == 'toggle':
            action = 'off' if current_state == 1 else 'on'
        elif action not in ['on', 'off']:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400
        
        # Toggle the outlet
        result = strip.toggle_plug(action, plug_num=outlet_num)
        
        return jsonify({
            'success': True,
            'action': action,
            'outlet_num': outlet_num
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/outlets/all', methods=['POST'])
def toggle_all_outlets():
    """API endpoint to toggle all outlets."""
    strip = get_power_strip()
    if not strip:
        return jsonify({'success': False, 'error': 'Failed to connect to power strip'}), 500
    
    try:
        data = request.get_json()
        action = data.get('action')  # 'on' or 'off'
        
        if action not in ['on', 'off']:
            return jsonify({'success': False, 'error': 'Invalid action. Must be "on" or "off"'}), 400
        
        # Get all outlet numbers
        info = get_outlet_info()
        if 'error' in info:
            return jsonify({'success': False, 'error': info['error']}), 500
        
        outlet_numbers = list(info['outlets'].keys())
        result = strip.toggle_plugs(action, plug_num_list=outlet_numbers)
        
        return jsonify({
            'success': True,
            'action': action
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/outlet/<int:outlet_num>/power', methods=['GET'])
def get_power_draw(outlet_num):
    """API endpoint to get power draw information for a specific outlet."""
    strip = get_power_strip()
    if not strip:
        return jsonify({'success': False, 'error': 'Failed to connect to power strip'}), 500
    
    try:
        energy_info = strip.get_realtime_energy_info(plug_num=outlet_num)
        
        # Format the response
        power_data = {}
        
        # Standard format
        if 'voltage' in energy_info:
            power_data['voltage'] = round(energy_info['voltage'], 2)
        if 'current' in energy_info:
            power_data['current'] = round(energy_info['current'], 3)
        if 'power' in energy_info:
            power_data['power'] = round(energy_info['power'], 2)
        if 'total' in energy_info:
            power_data['total'] = round(energy_info['total'], 3)
        
        # Millivolt/milliampere format
        if 'voltage_mv' in energy_info:
            power_data['voltage'] = round(energy_info['voltage_mv'] / 1000, 2)
        if 'current_ma' in energy_info:
            power_data['current'] = round(energy_info['current_ma'] / 1000, 3)
        if 'power_mw' in energy_info:
            power_data['power'] = round(energy_info['power_mw'] / 1000, 2)
            # Note: Total energy calculation may need adjustment based on actual device response
        if 'total_mw' in energy_info:
            power_data['total'] = round(energy_info['total_mw'], 3)
        
        # Get outlet name
        info = get_outlet_info()
        outlet_name = info.get('outlets', {}).get(outlet_num, {}).get('name', f'Outlet {outlet_num}')
        
        return jsonify({
            'success': True,
            'outlet_num': outlet_num,
            'outlet_name': outlet_name,
            'power_data': power_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Get IP from config or use default
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Flask web application...")
    print(f"Power Strip IP: {power_strip_ip}")
    print(f"Server will run on http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

