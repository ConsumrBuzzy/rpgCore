"""
DGT Core Engines Package
Unified display and simulation engines
"""

from .body import (
    TriModalEngine, BodyEngine, EngineConfig,
    DisplayDispatcher, DisplayMode, RenderPacket,
    TerminalBody, CockpitBody, PPUBody,
    create_tri_modal_engine, create_legacy_engine,
    GraphicsEngine, RenderFrame, TileBank, Viewport, RenderLayer,
    TRI_MODAL_AVAILABLE
)

__all__ = [
    "TriModalEngine", "BodyEngine", "EngineConfig",
    "DisplayDispatcher", "DisplayMode", "RenderPacket",
    "TerminalBody", "CockpitBody", "PPUBody",
    "create_tri_modal_engine", "create_legacy_engine",
    "GraphicsEngine", "RenderFrame", "TileBank", "Viewport", "RenderLayer",
    "TRI_MODAL_AVAILABLE"
]
