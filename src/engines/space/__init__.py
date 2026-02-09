"""
Space Engines Module

Newtonian Physics and Space Combat Systems

This module contains the space-specific engines that implement
the classic Asteroids-style physics within the DGT Platform's
sovereign 160x144 resolution constraint.
"""

from .asteroids_strategy import AsteroidsStrategy
from .physics_body import PhysicsBody
from .space_entity import SpaceEntity, EntityType
from .vector2 import Vector2

__all__ = [
    'AsteroidsStrategy',
    'PhysicsBody', 
    'SpaceEntity',
    'EntityType',
    'Vector2'
]
