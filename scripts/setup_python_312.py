#!/usr/bin/env python3
"""
Setup Python 3.12 Environment for DGT Platform

This script ensures the project is running on Python 3.12 and sets up a proper
virtual environment if needed. Run this to bootstrap the development environment.
"""

import os
import sys
from pathlib import Path

# Add src to path so we can import foundation tools
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from foundation import PythonVersionManager
except ImportError:
    print("❌ Cannot import foundation tools. This script must be run from the project root.")
    sys.exit(1)


def main():
    """Main setup function."""
    print("🏗️  DGT Platform Python 3.12 Setup")
    print("=" * 50)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    print(f"📁 Project root: {project_root}")
    
    # Initialize version manager
    version_mgr = PythonVersionManager(project_root)
    
    # Check current version
    print("\n🔍 Checking Python version...")
    is_valid, message = version_mgr.check_current_version()
    
    if is_valid:
        print(f"✅ Current Python version: {message}")
        
        # Check if we're in a venv
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Running in virtual environment")
        else:
            print("⚠️  Not running in virtual environment")
            print("   Consider creating a virtual environment for isolation")
    else:
        print(f"❌ {message}")
        print("\n🔧 Attempting to set up Python 3.12 environment...")
        
        # Try to set up venv
        if version_mgr.setup_or_validate_venv(auto_create=True):
            print("\n✅ Python 3.12 environment setup complete!")
            print("\n📋 Next steps:")
            print("   1. Activate the virtual environment:")
            
            # Find the venv that was created/validated
            venv_names = [".venv", "venv", "env", ".env"]
            for venv_name in venv_names:
                venv_path = project_root / venv_name
                if venv_path.exists():
                    is_valid, version_msg = version_mgr.check_venv_version(venv_path)
                    if is_valid:
                        if os.name == "nt":
                            activate_cmd = f".venv\\Scripts\\activate"
                        else:
                            activate_cmd = f"source .venv/bin/activate"
                        print(f"      {activate_cmd}")
                        break
            
            print("   2. Install dependencies:")
            print("      pip install -e .")
            print("   3. Run tests:")
            print("      python tests/verification/test_headless_derby.py")
        else:
            print("\n❌ Failed to set up Python 3.12 environment")
            print("   Please install Python 3.12 manually:")
            print("   - Windows: Download from python.org or use 'py -3.12'")
            print("   - Linux/macOS: Use package manager or python.org")
            sys.exit(1)
    
    # Final validation
    print("\n🔍 Final validation...")
    is_valid, message = version_mgr.check_current_version()
    if is_valid:
        print(f"✅ Environment validated: Python {message}")
        print("\n🎉 DGT Platform is ready for development!")
    else:
        print(f"❌ Environment validation failed: {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
