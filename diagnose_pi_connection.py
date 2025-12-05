#!/usr/bin/env python3
"""
Diagnostic script for Raspberry Pi connection issues.
Run this on the Raspberry Pi to diagnose connection problems.
"""

import sys
import socket
import subprocess
import platform

def test_ping(ip: str) -> bool:
    """Test if we can ping the device."""
    print(f"\n1. Testing ICMP connectivity (ping) to {ip}...")
    try:
        result = subprocess.run(
            ["ping", "-c", "3", ip],
            capture_output=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("   ✓ Ping successful")
            print(f"   Output: {result.stdout.decode()[:200]}")
            return True
        else:
            print(f"   ✗ Ping failed (return code: {result.returncode})")
            print(f"   Error: {result.stderr.decode()}")
            return False
    except Exception as e:
        print(f"   ✗ Ping error: {e}")
        return False

def test_tcp_connection(ip: str, port: int = 9999, timeout: float = 5.0):
    """Test TCP connection to the device."""
    print(f"\n2. Testing TCP connection to {ip}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        sock.connect((ip, port))
        print(f"   ✓ TCP connection successful")
        sock.close()
        return True, None
    except socket.timeout:
        error_msg = "Connection timeout"
        print(f"   ✗ {error_msg}")
        return False, error_msg
    except ConnectionRefusedError as e:
        error_msg = f"Connection refused: {e}"
        print(f"   ✗ {error_msg}")
        return False, error_msg
    except OSError as e:
        error_msg = f"OSError: {e}"
        print(f"   ✗ {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(f"   ✗ {error_msg}")
        return False, error_msg
    finally:
        try:
            sock.close()
        except:
            pass

def test_udp_connection(ip: str, port: int = 9999, timeout: float = 5.0):
    """Test UDP connection to the device."""
    print(f"\n3. Testing UDP connection to {ip}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    
    try:
        # Try to send a small test packet
        test_data = b"test"
        sock.sendto(test_data, (ip, port))
        print(f"   ✓ UDP packet sent successfully")
        
        # Try to receive (though device might not respond to test packet)
        try:
            data, addr = sock.recvfrom(1024)
            print(f"   ✓ Received response from {addr}")
        except socket.timeout:
            print(f"   ⚠ No response (this may be normal for test packet)")
        
        sock.close()
        return True, None
    except OSError as e:
        error_msg = f"OSError: {e}"
        print(f"   ✗ {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(f"   ✗ {error_msg}")
        return False, error_msg
    finally:
        try:
            sock.close()
        except:
            pass

def get_network_info():
    """Get network interface information."""
    print(f"\n4. Network interface information...")
    try:
        result = subprocess.run(
            ["ip", "addr", "show"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("   Network interfaces:")
            # Show relevant lines
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if 'inet ' in line and '127.0.0.1' not in line:
                    print(f"   {line.strip()}")
        else:
            # Fallback to ifconfig
            result = subprocess.run(
                ["ifconfig"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("   Network interfaces:")
                for line in result.stdout.split('\n'):
                    if 'inet ' in line and '127.0.0.1' not in line:
                        print(f"   {line.strip()}")
    except Exception as e:
        print(f"   Error getting network info: {e}")

def check_subnet(pi_ip: str, device_ip: str):
    """Check if Pi and device are on same subnet."""
    print(f"\n5. Checking subnet compatibility...")
    try:
        pi_parts = pi_ip.split('.')
        device_parts = device_ip.split('.')
        
        if len(pi_parts) == 4 and len(device_parts) == 4:
            pi_subnet = '.'.join(pi_parts[:3])
            device_subnet = '.'.join(device_parts[:3])
            
            print(f"   Pi IP subnet: {pi_subnet}.x")
            print(f"   Device IP subnet: {device_subnet}.x")
            
            if pi_subnet == device_subnet:
                print(f"   ✓ Same subnet - routing should work")
                return True
            else:
                print(f"   ✗ Different subnets - routing may be required")
                return False
        else:
            print(f"   ⚠ Could not determine subnet")
            return None
    except Exception as e:
        print(f"   Error checking subnet: {e}")
        return None

def get_local_ip():
    """Get local IP address."""
    try:
        # Try to connect to external server to determine local IP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except:
        return None

def check_firewall():
    """Check if firewall is blocking connections."""
    print(f"\n6. Checking firewall status...")
    try:
        # Check ufw (common on Raspberry Pi)
        result = subprocess.run(
            ["sudo", "ufw", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"   UFW Status: {output}")
            if "active" in output.lower():
                print(f"   ⚠ WARNING: UFW firewall is active!")
                print(f"   You may need to allow port 9999:")
                print(f"   sudo ufw allow 9999/udp")
                print(f"   sudo ufw allow 9999/tcp")
        else:
            print(f"   UFW not configured or not accessible")
    except Exception as e:
        print(f"   Could not check firewall: {e}")

def main():
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        ip = "192.168.50.137"
    
    print("=" * 70)
    print("Raspberry Pi - TP-Link HS300 Connection Diagnostic")
    print("=" * 70)
    print(f"\nTarget device: {ip}:9999")
    print(f"Platform: {platform.system()} {platform.release()}")
    
    # Get local IP
    local_ip = get_local_ip()
    if local_ip:
        print(f"Local IP: {local_ip}")
    
    # Run tests
    ping_ok = test_ping(ip)
    tcp_ok, tcp_error = test_tcp_connection(ip)
    udp_ok, udp_error = test_udp_connection(ip)
    
    # Additional diagnostics
    get_network_info()
    if local_ip:
        check_subnet(local_ip, ip)
    check_firewall()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Ping (ICMP):     {'✓ PASS' if ping_ok else '✗ FAIL'}")
    print(f"TCP (port 9999): {'✓ PASS' if tcp_ok else '✗ FAIL'}")
    print(f"UDP (port 9999): {'✓ PASS' if udp_ok else '✗ FAIL'}")
    
    if not ping_ok:
        print("\n⚠ CRITICAL: Cannot ping device!")
        print("   - Check network cable/WiFi connection")
        print("   - Verify device IP address is correct")
        print("   - Check if device is powered on")
    elif ping_ok and not tcp_ok and not udp_ok:
        print("\n⚠ DIAGNOSIS: Device is reachable (ping works) but socket connections fail.")
        print("   Possible causes:")
        print("   1. Device is in 'Cloud Only' mode (enable Local Control in Kasa app)")
        print("   2. Firewall blocking port 9999")
        print("   3. Device not listening on port 9999")
        print("   4. Network routing issue")
        print("\n   RECOMMENDED ACTIONS:")
        print("   1. Check Kasa app - enable 'Local Control'")
        print("   2. Check firewall: sudo ufw status")
        print("   3. Try: sudo ufw allow 9999/udp && sudo ufw allow 9999/tcp")
        print("   4. Verify device firmware is up to date")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

