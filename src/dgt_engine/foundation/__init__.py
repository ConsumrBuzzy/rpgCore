"""
Foundation Tier
Shared utilities, constants, and base classes.
"""

import sys
from pathlib import Path

# ADR 215: Python Version Check (Relaxed for 3.14 compatibility)
if sys.version_info < (3, 12, 0):
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    raise RuntimeError(
        f"DGT Platform requires Python 3.12.x or newer. Current version: {current_version}\n"
        "Please upgrade your Python environment."
    )

# Lazy loading of foundation components
_FOUNDATION_EXPORTS = {
    "Vector2", "Result", "Direction", "CollisionType",
}

__all__ = sorted(_FOUNDATION_EXPORTS)

def __getattr__(name: str):
    """Lazy-load foundation submodules and redirect to new structure."""

    # === NEW STRUCTURE REDIRECTS (Phase B Migration) ===
    # Redirect new foundation classes to game_engine.foundation
    new_foundation_mapping = {
        "BaseSystem": "base_system",
        "BaseComponent": "base_system",
        "SystemConfig": "base_system",
        "SystemStatus": "base_system",
        "PerformanceMetrics": "base_system",
        "Vector2Protocol": "protocols",
        "Vector3Protocol": "protocols",
        "EntityProtocol": "protocols",
        "GameStateProtocol": "protocols",
        "ClockProtocol": "protocols",
        "RenderPacketProtocol": "protocols",
        "ConfigProtocol": "protocols",
        "DGTRegistry": "registry",
        "RegistryType": "registry",
        "RegistryEntry": "registry",
    }

    if name in new_foundation_mapping:
        # Import from new game_engine.foundation structure
        module_name = new_foundation_mapping[name]
        import importlib
        try:
            mod = importlib.import_module(f"game_engine.foundation.{module_name}")
            return getattr(mod, name)
        except ImportError:
            pass  # Fall through to old structure

    # === OLD STRUCTURE IMPORTS (Legacy Support) ===
    if name == "Vector2":
        from .vector import Vector2
        return Vector2

    if name in {"Result"}:
        from .types import Result
        return Result

    if name in {"Direction", "CollisionType"}:
        from .constants import Direction, CollisionType
        return getattr(sys.modules[__name__], name) # Fallback for now

    raise AttributeError(f"module 'dgt_engine.foundation' has no attribute {name!r}")
