# Raspberry Pi Connection Troubleshooting Guide

## Quick Diagnostic

Run this diagnostic script on your Raspberry Pi:

```bash
python3 diagnose_pi_connection.py 192.168.50.137
```

## Common Issues and Solutions

### 1. Device Not Responding (Timeout/Connection Refused)

**Symptoms:**
- Ping works but socket connections fail
- UDP timeout
- TCP connection refused

**Solutions:**

#### A. Enable Local Control in Kasa App
1. Open Kasa mobile app
2. Select your HS300 power strip
3. Go to Device Settings (gear icon)
4. Look for "Local Control" or "Cloud Only" setting
5. **Enable "Local Control"** if disabled
6. Wait 30 seconds and try again

#### B. Check Firewall on Raspberry Pi
```bash
# Check firewall status
sudo ufw status

# If firewall is active, allow port 9999
sudo ufw allow 9999/udp
sudo ufw allow 9999/tcp

# Or temporarily disable firewall to test
sudo ufw disable
```

#### C. Verify Network Connectivity
```bash
# Test ping
ping -c 3 192.168.50.137

# Check if you're on the same subnet
ip addr show
# Look for your IP address - should be 192.168.50.x

# Test port connectivity
nc -zv -u 192.168.50.137 9999  # UDP
nc -zv 192.168.50.137 9999     # TCP
```

### 2. Wrong IP Address

**Check if device IP has changed:**
```bash
# Scan network for TP-Link devices
nmap -sn 192.168.50.0/24

# Or check router DHCP table
# Look for device named "HS300" or similar
```

**Update config.py:**
```python
POWER_STRIP_IP = "192.168.50.137"  # Update with correct IP
```

### 3. Network Routing Issues

**If Pi and device are on different subnets:**

```bash
# Check your IP
hostname -I

# Check device IP
ping 192.168.50.137

# If different subnets, you may need:
# - Router configuration
# - VPN/tunnel setup
# - Or ensure both are on same network
```

### 4. Device Needs Reset

**If nothing else works:**

1. **Reset the power strip:**
   - Hold reset button for 10 seconds
   - Device will restart

2. **Reconnect via Kasa app:**
   - Add device again in Kasa app
   - Ensure "Local Control" is enabled
   - Note the new IP address

3. **Update config.py with new IP**

### 5. Increase Timeout

**If connections are slow:**

Edit `config.py`:
```python
POWER_STRIP_TIMEOUT = 5.0  # Increase from 2.0 to 5.0
```

Or try UDP protocol:
```python
POWER_STRIP_PROTOCOL = "udp"  # Change from "tcp" to "udp"
```

## Testing Steps

1. **Run diagnostic:**
   ```bash
   python3 diagnose_pi_connection.py 192.168.50.137
   ```

2. **Test basic connectivity:**
   ```bash
   ping -c 3 192.168.50.137
   ```

3. **Test with Python directly:**
   ```bash
   python3 -c "from KasaSmartPowerStrip import SmartPowerStrip; s = SmartPowerStrip('192.168.50.137', timeout=5.0, protocol='udp'); print(s.get_system_info())"
   ```

4. **Check logs:**
   ```bash
   # Check system logs for network issues
   dmesg | tail -20
   journalctl -u NetworkManager -n 20
   ```

## Still Not Working?

1. **Verify device is online:**
   - Check Kasa app - device should show as online
   - Check device LED indicators

2. **Try from different device:**
   - Test from your Mac/PC to isolate Pi-specific issues
   - If works elsewhere, focus on Pi network config

3. **Check device firmware:**
   - Update via Kasa app if available
   - Some firmware versions have local control issues

4. **Network isolation:**
   - Ensure Pi and device are on same WiFi network
   - Check for guest network isolation
   - Verify no VLAN separation

## Quick Test Script

Create `test_connection.py`:
```python
#!/usr/bin/env python3
from KasaSmartPowerStrip import SmartPowerStrip
import sys

ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.50.137"

try:
    print(f"Connecting to {ip}...")
    strip = SmartPowerStrip(ip, timeout=10.0, protocol='udp')
    print("✓ Connected!")
    info = strip.get_system_info()
    print(f"Device: {info['system']['get_sysinfo']['alias']}")
except Exception as e:
    print(f"✗ Failed: {e}")
```

Run: `python3 test_connection.py 192.168.50.137`


