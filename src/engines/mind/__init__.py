"""
Mind Engine - D&D Logic with Command Pattern

Implements turn-based D20 combat and command processing
following the Result[T] pattern for clean error handling.
"""

from .dd_engine import DDEngine, DDEngineFactory

__all__ = [
    "DDEngine",
    "DDEngineFactory"
]
