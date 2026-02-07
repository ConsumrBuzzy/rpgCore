"""
Body Engine Module - The Body Pillar

160x144 Game Boy parity rendering with layer composition.
The Body Engine transforms the Mind's state into visual representation.

Key Features:
- Game Boy parity PPU rendering
- Multi-layer composition system
- Viewport management and camera following
- Subtitle overlay support
- Performance-optimized rendering
"""

from .graphics_engine import (
    GraphicsEngine, RenderFrame, TileBank, Viewport, RenderLayer,
    GraphicsEngineFactory, GraphicsEngineSync
)

__all__ = [
    "GraphicsEngine", "RenderFrame", "TileBank", "Viewport", "RenderLayer",
    "GraphicsEngineFactory", "GraphicsEngineSync"
]
