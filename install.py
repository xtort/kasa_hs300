#!/usr/bin/env python3
"""
Installation script for TP-Link HS300 Power Strip CLI.

This script helps users install and configure the CLI application.
"""

import os
import sys
import subprocess
import shutil


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(
        f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")

    try:
        # Check if pip is available
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                       check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip not found. Please install pip first.")
        return False

    # Install dependencies (currently none, but structure is ready)
    print("✅ No external dependencies required")
    return True


def create_config_file():
    """Create a configuration file if it doesn't exist."""
    config_content = '''#!/usr/bin/env python3
"""
Configuration file for the TP-Link HS300 Power Strip CLI.
"""

# Power Strip Configuration
POWER_STRIP_IP = "192.168.2.3"  # Change this to your power strip's IP
POWER_STRIP_TIMEOUT = 2.0
POWER_STRIP_PROTOCOL = "tcp"  # 'tcp' or 'udp'

# CLI Configuration
CLI_REFRESH_DELAY = 1.0  # seconds
CLI_SHOW_EMOJIS = True   # Enable/disable emoji indicators

# Outlet Configuration
MAX_OUTLETS = 6  # Maximum number of outlets on HS300
DEFAULT_OUTLET_NAMES = {
    1: "Outlet 1",
    2: "Outlet 2", 
    3: "Outlet 3",
    4: "Outlet 4",
    5: "Outlet 5",
    6: "Outlet 6"
}
'''

    if not os.path.exists("config.py"):
        with open("config.py", "w") as f:
            f.write(config_content)
        print("✅ Created config.py")
    else:
        print("ℹ️  config.py already exists")


def make_executable():
    """Make the CLI script executable."""
    cli_script = "src/kasa_cli.py"
    if os.path.exists(cli_script):
        try:
            os.chmod(cli_script, 0o755)
            print("✅ Made CLI script executable")
        except Exception as e:
            print(f"⚠️  Could not make script executable: {e}")
    else:
        print("❌ CLI script not found")


def test_installation():
    """Test the installation by importing the modules."""
    print("\n🧪 Testing installation...")

    try:
        # Test importing the CLI module
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from src.kasa_cli import KasaPowerStripCLI
        print("✅ CLI module imported successfully")

        # Test importing the original library
        from KasaSmartPowerStrip import SmartPowerStrip
        print("✅ Original library imported successfully")

        return True
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False


def show_usage_instructions():
    """Show usage instructions."""
    print("\n🎉 Installation completed successfully!")
    print("\n📖 Usage Instructions:")
    print("=" * 50)
    print("1. Configure your power strip IP address:")
    print("   - Edit config.py and change POWER_STRIP_IP")
    print("   - Or use command line: --ip 192.168.2.3")
    print("\n2. Run the CLI:")
    print("   python src/kasa_cli.py --ip 192.168.2.3")
    print("   or")
    print("   python run_cli.py")
    print("\n3. Run the demo:")
    print("   python demo.py")
    print("\n4. Run tests:")
    print("   python -m pytest tests/")
    print("\n📚 For more information, see README.md")


def main():
    """Main installation function."""
    print("🚀 TP-Link HS300 Power Strip CLI Installer")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        return False

    # Install dependencies
    if not install_dependencies():
        return False

    # Create config file
    create_config_file()

    # Make executable
    make_executable()

    # Test installation
    if not test_installation():
        return False

    # Show usage instructions
    show_usage_instructions()

    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Installation completed successfully!")
        else:
            print("\n❌ Installation failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInstallation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed with error: {e}")
        sys.exit(1)
