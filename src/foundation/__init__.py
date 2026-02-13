"""
Foundation Tier
Shared utilities, constants, and base classes.
"""

import sys

# ADR 215: Python 3.12 Version Lockdown
# Protects the DGT Platform from version drift and MRO compatibility issues
if not ((3, 12, 0) <= sys.version_info < (3, 13, 0)):
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    raise RuntimeError(
        f"DGT Platform requires Python 3.12.x. Current version: {current_version}\n"
        "This ensures deterministic behavior and protects against version drift.\n"
        "Please install Python 3.12 and create a fresh virtual environment."
    )
