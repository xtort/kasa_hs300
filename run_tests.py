#!/usr/bin/env python3
"""
Test runner script for the Kasa HS300 CLI project.

This script can be used to run tests with uv or pytest directly.
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests_with_uv():
    """Run tests using uv."""
    try:
        # Check if uv is available
        result = subprocess.run([sys.executable, "-m", "uv", "--version"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ uv not found. Please install uv first.")
            return False
        
        print("🚀 Running tests with uv...")
        
        # Run tests with uv
        cmd = [sys.executable, "-m", "uv", "run", "pytest", "tests/", "-v"]
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        
        return result.returncode == 0
        
    except FileNotFoundError:
        print("❌ uv not found. Please install uv first.")
        return False
    except Exception as e:
        print(f"❌ Error running tests with uv: {e}")
        return False

def run_tests_with_pytest():
    """Run tests using pytest directly."""
    try:
        print("🚀 Running tests with pytest...")
        
        # Run tests with pytest
        cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        
        return result.returncode == 0
        
    except FileNotFoundError:
        print("❌ pytest not found. Please install pytest first.")
        return False
    except Exception as e:
        print(f"❌ Error running tests with pytest: {e}")
        return False

def run_tests_with_unittest():
    """Run tests using unittest directly."""
    try:
        print("🚀 Running tests with unittest...")
        
        # Add the current directory to the path
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Run tests with unittest
        cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests with unittest: {e}")
        return False

def main():
    """Main function to run tests."""
    print("🧪 Kasa HS300 CLI Test Runner")
    print("=" * 40)
    
    # Try different test runners in order of preference
    runners = [
        ("uv", run_tests_with_uv),
        ("pytest", run_tests_with_pytest),
        ("unittest", run_tests_with_unittest),
    ]
    
    for name, runner_func in runners:
        print(f"\nTrying {name}...")
        if runner_func():
            print(f"\n✅ Tests completed successfully with {name}!")
            return 0
        else:
            print(f"⚠️  {name} failed or not available, trying next option...")
    
    print("\n❌ All test runners failed. Please check your installation.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
