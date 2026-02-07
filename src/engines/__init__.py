"""
D&D Engine - The Mind Pillar

Deterministic D20 logic, state mutation, and rule enforcement.
Single Source of Truth for all game state.
"""

from .dd_engine import DD_Engine, GameState, MovementIntent, InteractionIntent, ValidationResult
from .world_engine import WorldEngine, WorldEngineFactory, TileType, TileData, WorldDelta

__all__ = [
    'DD_Engine',
    'GameState', 
    'MovementIntent',
    'InteractionIntent',
    'ValidationResult',
    'WorldEngine',
    'WorldEngineFactory',
    'TileType',
    'TileData',
    'WorldDelta'
]
