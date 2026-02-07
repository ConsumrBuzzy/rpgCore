"""
Actors Module - The Actor Pillar

The Voyager - autonomous pathfinding and intent generation with STATE_PONDERING support.
The Actor bridges the deterministic world and the chaotic narrative through discovery
and pondering of Interest Points.

Key Features:
- A* pathfinding with confidence scoring
- State machine with STATE_PONDERING for LLM processing
- Autonomous movie script navigation
- Interest Point discovery and manifestation
- Performance tracking and optimization
"""

from .voyager import (
    Voyager, NavigationGoal, PathfindingNode, PathfindingNavigator, IntentGenerator,
    VoyagerFactory, VoyagerSync
)

__all__ = [
    "Voyager", "NavigationGoal", "PathfindingNode", "PathfindingNavigator", "IntentGenerator",
    "VoyagerFactory", "VoyagerSync"
]
