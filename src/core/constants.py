"""
Core Constants - System Configuration and Magic Numbers
LEGACY SHIM - Delegates to src.dgt_core.kernel.constants

All system constants, configuration values, and magic numbers
centralized for maintainability and consistency.
"""
import warnings
import sys
import importlib

# Ensure the source module is available
try:
    # Direct module import to avoid import * issues
    kernel_constants = importlib.import_module('src.dgt_core.kernel.constants')
    
    # Copy all attributes from kernel constants to this module
    for attr_name in dir(kernel_constants):
        if not attr_name.startswith('_'):
            globals()[attr_name] = getattr(kernel_constants, attr_name)
    
    # Verify critical constants are available
    required_constants = [
        'EMERGENCY_SAVE_PREFIX',
        'LOG_LEVEL_DEFAULT', 
        'SOVEREIGN_WIDTH',
        'SOVEREIGN_HEIGHT',
        'LOG_FORMAT'
    ]
    
    missing_constants = []
    for const in required_constants:
        if const not in globals():
            missing_constants.append(const)
    
    if missing_constants:
        raise ImportError(f"Missing required constants: {missing_constants}")
    
except ImportError as e:
    # Fallback - provide minimal constants to prevent system failure
    warnings.warn(f"Core constants shim failed: {e}", RuntimeWarning)
    
    # Minimal fallback constants
    EMERGENCY_SAVE_PREFIX = "emergency_save"
    LOG_LEVEL_DEFAULT = "INFO"
    LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    SOVEREIGN_WIDTH = 160
    SOVEREIGN_HEIGHT = 144
