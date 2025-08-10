# KasaSmartPowerStrip.py Enhancements

This document outlines the enhancements made to the original `KasaSmartPowerStrip.py` library.

## 🎯 **Key Enhancements**

### **1. Modern Python Features**
- ✅ **Type Hints**: Added comprehensive type annotations for all methods
- ✅ **Python 3 Style**: Updated to use modern Python 3 class syntax
- ✅ **Better Documentation**: Added detailed docstrings for all methods
- ✅ **Error Handling**: Improved exception handling with specific error types

### **2. Enhanced Error Handling**
- ✅ **Connection Errors**: Specific `ConnectionError` exceptions for connection failures
- ✅ **Validation**: Input validation with descriptive error messages
- ✅ **Graceful Fallbacks**: TCP fallback when UDP fails for system info
- ✅ **Resource Management**: Proper socket cleanup with try/finally blocks

### **3. New Utility Methods**

#### **`get_all_plugs_status()`**
```python
# Get status of all plugs at once
status = power_strip.get_all_plugs_status()
# Returns: {1: {'name': 'Outlet 1', 'state': 1, 'id': '00', 'on_time': 3600}, ...}
```

#### **`turn_all_plugs(state)`**
```python
# Turn all plugs on or off simultaneously
power_strip.turn_all_plugs('on')   # Turn all plugs on
power_strip.turn_all_plugs('off')  # Turn all plugs off
```

#### **`get_plug_count()`**
```python
# Get the number of plugs on the power strip
count = power_strip.get_plug_count()  # Returns: 6
```

#### **`is_plug_on(plug_num/plug_name)`**
```python
# Check if a specific plug is on
is_on = power_strip.is_plug_on(plug_num=1)           # By number
is_on = power_strip.is_plug_on(plug_name='Lamp')     # By name
```

### **4. Improved Method Signatures**

#### **Better Type Annotations**
```python
# Before
def toggle_plug(self, state, plug_num=None, plug_name=None):

# After  
def toggle_plug(self, state: str, plug_num: Optional[int] = None,
               plug_name: Optional[str] = None) -> Dict[str, Any]:
```

#### **Enhanced Documentation**
```python
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
```

### **5. Code Quality Improvements**

#### **Better String Formatting**
```python
# Before
wifi_command = '{"netif":{"set_stainfo":{"ssid":"' + ssid + '","password":"' + \
               psk + '","key_type":' + key_type + '}}}'

# After
wifi_command = (
    '{"netif":{"set_stainfo":{"ssid":"' + ssid + 
    '","password":"' + psk + '","key_type":' + key_type + '}}}'
)
```

#### **Improved Error Messages**
```python
# Before
raise ValueError('Unable to find plug with name ' + plug_name)

# After
raise ValueError(f'Unable to find plug with name {plug_name}')
```

#### **Resource Management**
```python
# Before
sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_tcp.settimeout(self.timeout)
sock_tcp.connect((self.ip, self.port))
sock_tcp.send(self._encrypt_command(command))
data = sock_tcp.recv(2048)
sock_tcp.close()
return json.loads(self._decrypt_command(data[4:]))

# After
sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_tcp.settimeout(self.timeout)
try:
    sock_tcp.connect((self.ip, self.port))
    sock_tcp.send(self._encrypt_command(command))
    data = sock_tcp.recv(2048)
    return json.loads(self._decrypt_command(data[4:]))
finally:
    sock_tcp.close()
```

### **6. Backward Compatibility**

All enhancements maintain **100% backward compatibility** with the original API:

- ✅ All existing method signatures preserved
- ✅ All existing functionality maintained
- ✅ No breaking changes introduced
- ✅ Original behavior unchanged

### **7. Additional Features**

#### **Enhanced Initialization**
```python
# Better error handling during initialization
try:
    self.sys_info = self.get_system_info()['system']['get_sysinfo']
    if not self.device_id:
        self.device_id = self.sys_info['deviceId']
except Exception as e:
    raise ConnectionError(f"Failed to connect to power strip at {ip}: {e}")
```

#### **Improved State Management**
```python
# Better state conversion with validation
def _get_plug_state_int(self, state: str, reverse: bool = False) -> int:
    state_lower = state.lower()
    if state_lower == 'on':
        return 0 if reverse else 1
    elif state_lower == 'off':
        return 1 if reverse else 0
    else:
        raise ValueError("Invalid state, must be 'on' or 'off'")
```

## 🚀 **Usage Examples**

### **New Utility Methods**
```python
from KasaSmartPowerStrip import SmartPowerStrip

# Initialize
power_strip = SmartPowerStrip('192.168.2.3')

# Get all plug statuses
all_status = power_strip.get_all_plugs_status()
for plug_num, status in all_status.items():
    print(f"Plug {plug_num}: {status['name']} - {'ON' if status['state'] else 'OFF'}")

# Turn all plugs on
power_strip.turn_all_plugs('on')

# Check if specific plug is on
if power_strip.is_plug_on(plug_num=1):
    print("Plug 1 is currently ON")

# Get plug count
print(f"Power strip has {power_strip.get_plug_count()} plugs")
```

### **Enhanced Error Handling**
```python
try:
    power_strip = SmartPowerStrip('192.168.2.3')
except ConnectionError as e:
    print(f"Connection failed: {e}")
except ValueError as e:
    print(f"Invalid configuration: {e}")
```

## 📊 **Benefits**

1. **Better Developer Experience**: Type hints and documentation
2. **Improved Reliability**: Better error handling and resource management
3. **Enhanced Functionality**: New utility methods for common operations
4. **Maintainability**: Cleaner, more readable code
5. **Future-Proof**: Modern Python features and best practices

## 🔄 **Migration**

No migration required! The enhanced library is a drop-in replacement for the original:

```python
# Original code continues to work unchanged
from KasaSmartPowerStrip import SmartPowerStrip
power_strip = SmartPowerStrip('192.168.2.3')
power_strip.toggle_plug('on', plug_num=1)
```

All existing code will work exactly as before, but now with additional features and better error handling.
