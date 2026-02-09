"""
Engines Module - The Three Pillars

Service-Oriented Architecture implementation of the Four-Pillar System:
- World Engine: Deterministic world generation with Chaos-Seed Protocol
- Mind Engine: D&D logic with Command Pattern
- Body Engine: 160x144 PPU rendering

Each engine implements the Facade pattern for clean interfaces and
complete decoupling between pillars.
"""

from .mind import DDEngine, DDEngineFactory, DDEngineSync
from .body import GraphicsEngine, GraphicsEngineFactory, GraphicsEngineSync

__all__ = [
    # Mind Engine  
    "DDEngine", "DDEngineFactory", "DDEngineSync",
    
    # Body Engine
    "GraphicsEngine", "GraphicsEngineFactory", "GraphicsEngineSync"
]
