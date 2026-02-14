"""
DGT Graphics Engine — Backward Compatibility Layer

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from `game_engine.systems.graphics` instead.

Provides all graphics systems (PixelRenderer, TileBank, FXSystem, ParticleEffects, ExhaustSystem)
with backward-compatible imports for legacy code.

Example:
    # Old (still works, but deprecated):
    from dgt_engine.systems.graphics import PixelRenderer

    # New (preferred):
    from game_engine.systems.graphics import PixelRenderer
"""

from .__compat__ import *  # noqa: F401, F403
