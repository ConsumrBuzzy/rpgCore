"""
Graphics Engine - The Body Pillar (PPU Implementation)
LEGACY SHIM - Delegates to src.dgt_core.engines.body.graphics_engine

This shim ensures backward compatibility while the system migrates to the DGT SDK.
"""

import warnings

# Shim to the new DGT SDK
from src.dgt_core.engines.body.graphics_engine import (
    GraphicsEngine, RenderFrame, TileBank, Viewport,
    GraphicsEngineFactory, GraphicsEngineSync, RenderLayer
)

# Warn on import
warnings.warn(
    "Importing from src.engines.body.graphics_engine is deprecated. Use src.dgt_core.engines.body.graphics_engine instead.", 
    DeprecationWarning, 
    stacklevel=2
)
