#!/usr/bin/env python3
"""
Flask web application for controlling TP-Link HS300 Smart Power Strip.

This web application provides a browser-based interface for managing individual
outlets on a TP-Link HS300 power strip, including viewing status, controlling
outlets, and monitoring power draw.
"""

import sys
import os
import json
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

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# Global power strip connections cache (power_strip_id -> SmartPowerStrip instance)
power_strip_cache: Dict[str, Optional[SmartPowerStrip]] = {}


def load_web_config() -> Dict:
    """Load web app configuration from JSON file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading config file: {e}")
            return {}
    return {}


def save_web_config(config_data: Dict) -> bool:
    """Save web app configuration to JSON file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=2)
        return True
    except IOError as e:
        print(f"Error writing config file: {e}")
        return False


def get_default_power_strip_config() -> Dict:
    """Get default power strip configuration (for migration from old config)."""
    web_config = load_web_config()
    
    # Check if we have the new format (power_strips list)
    if 'power_strips' in web_config and isinstance(web_config['power_strips'], list):
        return web_config
    
    # Migrate from old format (single power_strip_ip)
    default_ip = web_config.get('power_strip_ip', getattr(config, 'POWER_STRIP_IP', '192.168.50.137'))
    
    return {
        'power_strips': [
            {
                'id': 'default',
                'name': 'Power Strip 1',
                'ip_address': default_ip
            }
        ],
        'active_power_strip_id': 'default'
    }


def get_power_strip_by_id(power_strip_id: Optional[str] = None) -> Optional[SmartPowerStrip]:
    """Get or create power strip connection by ID."""
    config_data = get_default_power_strip_config()
    power_strips = config_data.get('power_strips', [])
    
    # If no ID provided, use active one
    if not power_strip_id:
        power_strip_id = config_data.get('active_power_strip_id')
        if not power_strip_id and power_strips:
            power_strip_id = power_strips[0].get('id')
    
    if not power_strip_id:
        return None
    
    # Check cache first
    if power_strip_id in power_strip_cache:
        return power_strip_cache[power_strip_id]
    
    # Find power strip config
    power_strip_config = None
    for ps in power_strips:
        if ps.get('id') == power_strip_id:
            power_strip_config = ps
            break
    
    if not power_strip_config:
        return None
    
    # Create connection
    ip_address = power_strip_config.get('ip_address')
    if not ip_address:
        return None
    
    try:
        power_strip = SmartPowerStrip(ip_address)
        power_strip_cache[power_strip_id] = power_strip
        return power_strip
    except Exception as e:
        print(f"Failed to connect to power strip {power_strip_id} at {ip_address}: {e}")
        power_strip_cache[power_strip_id] = None
        return None


def reset_power_strip_connection(power_strip_id: Optional[str] = None):
    """Reset the power strip connection (useful when IP changes)."""
    if power_strip_id:
        power_strip_cache.pop(power_strip_id, None)
    else:
        power_strip_cache.clear()


def get_outlet_info(power_strip_id: Optional[str] = None) -> Dict:
    """Get outlet information from the power strip."""
    strip = get_power_strip_by_id(power_strip_id)
    if not strip:
        return {'error': 'Failed to connect to power strip'}
    
    config_data = get_default_power_strip_config()
    power_strips = config_data.get('power_strips', [])
    
    # Find power strip config for IP address
    if not power_strip_id:
        power_strip_id = config_data.get('active_power_strip_id')
    
    power_strip_config = None
    for ps in power_strips:
        if ps.get('id') == power_strip_id:
            power_strip_config = ps
            break
    
    ip_address = power_strip_config.get('ip_address', 'Unknown') if power_strip_config else 'Unknown'
    
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
            'ip_address': ip_address,
            'power_strip_id': power_strip_id,
            'power_strip_name': power_strip_config.get('name', 'Unknown') if power_strip_config else 'Unknown'
        }
    except Exception as e:
        return {'error': str(e)}


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/power-table')
def power_table():
    """Power table page showing all outlets' power draw."""
    return render_template('power_table.html')


@app.route('/api/outlets', methods=['GET'])
def get_outlets():
    """API endpoint to get all outlet information."""
    power_strip_id = request.args.get('power_strip_id')
    info = get_outlet_info(power_strip_id)
    return jsonify(info)


@app.route('/api/outlet/<int:outlet_num>/toggle', methods=['POST'])
def toggle_outlet(outlet_num):
    """API endpoint to toggle a specific outlet."""
    try:
        data = request.get_json() or {}
        power_strip_id = data.get('power_strip_id') or request.args.get('power_strip_id')
        action = data.get('action', 'toggle')  # 'on', 'off', or 'toggle'
        
        strip = get_power_strip_by_id(power_strip_id)
        if not strip:
            return jsonify({'success': False, 'error': 'Failed to connect to power strip'}), 500
        
        # Get current state
        info = get_outlet_info(power_strip_id)
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
        strip.toggle_plug(action, plug_num=outlet_num)
        
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
    try:
        data = request.get_json() or {}
        power_strip_id = data.get('power_strip_id') or request.args.get('power_strip_id')
        action = data.get('action')  # 'on' or 'off'
        
        if action not in ['on', 'off']:
            return jsonify({'success': False, 'error': 'Invalid action. Must be "on" or "off"'}), 400
        
        strip = get_power_strip_by_id(power_strip_id)
        if not strip:
            return jsonify({'success': False, 'error': 'Failed to connect to power strip'}), 500
        
        # Get all outlet numbers
        info = get_outlet_info(power_strip_id)
        if 'error' in info:
            return jsonify({'success': False, 'error': info['error']}), 500
        
        outlet_numbers = list(info['outlets'].keys())
        strip.toggle_plugs(action, plug_num_list=outlet_numbers)
        
        return jsonify({
            'success': True,
            'action': action
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/outlets/all/power', methods=['GET'])
def get_all_power_draw():
    """API endpoint to get power draw information for all outlets."""
    power_strip_id = request.args.get('power_strip_id')
    strip = get_power_strip_by_id(power_strip_id)
    if not strip:
        return jsonify({'success': False, 'error': 'Failed to connect to power strip'}), 500
    
    try:
        # Get outlet information to know how many outlets exist
        info = get_outlet_info(power_strip_id)
        if 'error' in info:
            return jsonify({'success': False, 'error': info['error']}), 500
        
        outlets = info['outlets']
        all_power_data = []
        
        # Get power data for each outlet
        for outlet_num in sorted(outlets.keys()):
            try:
                energy_info = strip.get_realtime_energy_info(plug_num=outlet_num)
                outlet_name = outlets[outlet_num]['name']
                
                # Format the power data (same logic as single outlet endpoint)
                power_data = {
                    'outlet_num': outlet_num,
                    'outlet_name': outlet_name
                }
                
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
                if 'total_mw' in energy_info:
                    power_data['total'] = round(energy_info['total_mw'], 3)
                
                all_power_data.append(power_data)
            except Exception as e:
                # If one outlet fails, continue with others but log the error
                all_power_data.append({
                    'outlet_num': outlet_num,
                    'outlet_name': outlets[outlet_num].get('name', f'Outlet {outlet_num}'),
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'power_data': all_power_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/api/outlet/<int:outlet_num>/power', methods=['GET'])
def get_power_draw(outlet_num):
    """API endpoint to get power draw information for a specific outlet."""
    power_strip_id = request.args.get('power_strip_id')
    strip = get_power_strip_by_id(power_strip_id)
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
        info = get_outlet_info(power_strip_id)
        outlet_name = info.get('outlets', {}).get(outlet_num, {}).get('name', f'Outlet {outlet_num}')
        
        return jsonify({
            'success': True,
            'outlet_num': outlet_num,
            'outlet_name': outlet_name,
            'power_data': power_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """API endpoint to get current configuration."""
    config_data = get_default_power_strip_config()
    
    return jsonify({
        'success': True,
        'power_strips': config_data.get('power_strips', []),
        'active_power_strip_id': config_data.get('active_power_strip_id')
    })


@app.route('/api/config/power-strips', methods=['GET'])
def list_power_strips():
    """API endpoint to list all power strips."""
    config_data = get_default_power_strip_config()
    return jsonify({
        'success': True,
        'power_strips': config_data.get('power_strips', []),
        'active_power_strip_id': config_data.get('active_power_strip_id')
    })


@app.route('/api/config/power-strips', methods=['POST'])
def add_power_strip():
    """API endpoint to add a new power strip."""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        ip_address = data.get('ip_address', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Name cannot be empty'}), 400
        
        if not ip_address:
            return jsonify({'success': False, 'error': 'IP address cannot be empty'}), 400
        
        # Validate IP address format
        ip_parts = ip_address.split('.')
        if len(ip_parts) != 4:
            return jsonify({'success': False, 'error': 'Invalid IP address format'}), 400
        
        try:
            for part in ip_parts:
                num = int(part)
                if num < 0 or num > 255:
                    raise ValueError()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid IP address format'}), 400
        
        config_data = get_default_power_strip_config()
        power_strips = config_data.get('power_strips', [])
        
        # Generate unique ID
        import uuid
        power_strip_id = str(uuid.uuid4())[:8]
        
        # Check for duplicate IP
        for ps in power_strips:
            if ps.get('ip_address') == ip_address:
                return jsonify({'success': False, 'error': 'A power strip with this IP address already exists'}), 400
        
        # Add new power strip
        new_power_strip = {
            'id': power_strip_id,
            'name': name,
            'ip_address': ip_address
        }
        power_strips.append(new_power_strip)
        config_data['power_strips'] = power_strips
        
        # Set as active if it's the first one
        if not config_data.get('active_power_strip_id'):
            config_data['active_power_strip_id'] = power_strip_id
        
        if not save_web_config(config_data):
            return jsonify({'success': False, 'error': 'Failed to save configuration'}), 500
        
        # Test connection
        test_strip = get_power_strip_by_id(power_strip_id)
        if test_strip is None:
            return jsonify({
                'success': True,
                'power_strip': new_power_strip,
                'warning': 'Power strip added but connection test failed. Please verify IP address.'
            })
        
        return jsonify({
            'success': True,
            'power_strip': new_power_strip,
            'message': 'Power strip added successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config/power-strips/<power_strip_id>', methods=['PUT'])
def update_power_strip(power_strip_id):
    """API endpoint to update a power strip."""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        ip_address = data.get('ip_address', '').strip()
        
        config_data = get_default_power_strip_config()
        power_strips = config_data.get('power_strips', [])
        
        # Find power strip
        power_strip_index = None
        for i, ps in enumerate(power_strips):
            if ps.get('id') == power_strip_id:
                power_strip_index = i
                break
        
        if power_strip_index is None:
            return jsonify({'success': False, 'error': 'Power strip not found'}), 404
        
        # Update fields
        if name:
            power_strips[power_strip_index]['name'] = name
        
        if ip_address:
            # Validate IP address format
            ip_parts = ip_address.split('.')
            if len(ip_parts) != 4:
                return jsonify({'success': False, 'error': 'Invalid IP address format'}), 400
            
            try:
                for part in ip_parts:
                    num = int(part)
                    if num < 0 or num > 255:
                        raise ValueError()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid IP address format'}), 400
            
            # Check for duplicate IP (excluding current)
            for ps in power_strips:
                if ps.get('id') != power_strip_id and ps.get('ip_address') == ip_address:
                    return jsonify({'success': False, 'error': 'A power strip with this IP address already exists'}), 400
            
            power_strips[power_strip_index]['ip_address'] = ip_address
        
        config_data['power_strips'] = power_strips
        
        if not save_web_config(config_data):
            return jsonify({'success': False, 'error': 'Failed to save configuration'}), 500
        
        # Reset connection for this power strip
        reset_power_strip_connection(power_strip_id)
        
        # Test connection if IP changed
        if ip_address:
            test_strip = get_power_strip_by_id(power_strip_id)
            if test_strip is None:
                return jsonify({
                    'success': True,
                    'power_strip': power_strips[power_strip_index],
                    'warning': 'Configuration updated but connection test failed. Please verify IP address.'
                })
        
        return jsonify({
            'success': True,
            'power_strip': power_strips[power_strip_index],
            'message': 'Power strip updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config/power-strips/<power_strip_id>', methods=['DELETE'])
def delete_power_strip(power_strip_id):
    """API endpoint to delete a power strip."""
    try:
        config_data = get_default_power_strip_config()
        power_strips = config_data.get('power_strips', [])
        
        # Find and remove power strip
        power_strips = [ps for ps in power_strips if ps.get('id') != power_strip_id]
        
        if len(power_strips) == len(config_data.get('power_strips', [])):
            return jsonify({'success': False, 'error': 'Power strip not found'}), 404
        
        # If deleting active one, set first as active
        if config_data.get('active_power_strip_id') == power_strip_id:
            if power_strips:
                config_data['active_power_strip_id'] = power_strips[0].get('id')
            else:
                config_data.pop('active_power_strip_id', None)
        
        config_data['power_strips'] = power_strips
        
        if not save_web_config(config_data):
            return jsonify({'success': False, 'error': 'Failed to save configuration'}), 500
        
        # Remove from cache
        reset_power_strip_connection(power_strip_id)
        
        return jsonify({
            'success': True,
            'message': 'Power strip deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config/active', methods=['POST'])
def set_active_power_strip():
    """API endpoint to set the active power strip."""
    try:
        data = request.get_json()
        power_strip_id = data.get('power_strip_id')
        
        if not power_strip_id:
            return jsonify({'success': False, 'error': 'power_strip_id is required'}), 400
        
        config_data = get_default_power_strip_config()
        power_strips = config_data.get('power_strips', [])
        
        # Verify power strip exists
        power_strip_exists = any(ps.get('id') == power_strip_id for ps in power_strips)
        if not power_strip_exists:
            return jsonify({'success': False, 'error': 'Power strip not found'}), 404
        
        config_data['active_power_strip_id'] = power_strip_id
        
        if not save_web_config(config_data):
            return jsonify({'success': False, 'error': 'Failed to save configuration'}), 500
        
        return jsonify({
            'success': True,
            'active_power_strip_id': power_strip_id,
            'message': 'Active power strip updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Get IP from config or use default
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    config_data = get_default_power_strip_config()
    power_strips = config_data.get('power_strips', [])
    
    print("Starting Flask web application...")
    if power_strips:
        print(f"Configured power strips: {len(power_strips)}")
        for ps in power_strips:
            print(f"  - {ps.get('name', 'Unknown')}: {ps.get('ip_address', 'Unknown')}")
    else:
        print("No power strips configured")
    print(f"Server will run on http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

