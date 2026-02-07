"""
DGT Core - The Unified Display Engine
Tri-Modal Display Suite with Universal Packet Architecture

ADR 120: Tri-Modal Rendering Bridge
ADR 122: Universal Packet Enforcement
"""

from .engines.body import (
    # Unified Engine
    TriModalEngine, BodyEngine, EngineConfig,
    
    # Display Bodies
    DisplayDispatcher, DisplayMode, RenderPacket,
    TerminalBody, CockpitBody, PPUBody,
    
    # Factory Functions
    create_tri_modal_engine, create_legacy_engine,
    
    # Legacy Graphics Engine (frozen artifact)
    GraphicsEngine, RenderFrame, TileBank, Viewport, RenderLayer,
    
    # Availability
    TRI_MODAL_AVAILABLE
)

__version__ = "2.0.0"
__all__ = [
    # Unified Engine
    "TriModalEngine", "BodyEngine", "EngineConfig",
    
    # Display System
    "DisplayDispatcher", "DisplayMode", "RenderPacket",
    "TerminalBody", "CockpitBody", "PPUBody",
    
    # Factory Functions
    "create_tri_modal_engine", "create_legacy_engine",
    
    # Legacy (maintained for compatibility)
    "GraphicsEngine", "RenderFrame", "TileBank", "Viewport", "RenderLayer",
    
    # Status
    "TRI_MODAL_AVAILABLE"
]
