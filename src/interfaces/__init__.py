"""
Interfaces Module - Protocol Definitions

This module contains formal protocol definitions for the DGT Platform,
ensuring proper dependency inversion and interface segregation.
"""

from .entity_protocol import (
    EntityProtocol,
    RenderableProtocol,
    CollectableProtocol,
    PhysicsProtocol,
    ScrapEntityProtocol,
    ShipEntityProtocol,
    AsteroidEntityProtocol
)

__all__ = [
    'EntityProtocol',
    'RenderableProtocol', 
    'CollectableProtocol',
    'PhysicsProtocol',
    'ScrapEntityProtocol',
    'ShipEntityProtocol',
    'AsteroidEntityProtocol'
]
