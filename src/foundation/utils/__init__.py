"""
Utils Module - The Plumbing

Utility modules that support the core system:
- Persistence: Delta-based state management with compression
- Logger: Centralized logging with Loguru and Rich
- Asset Loader: Minimal stub for asset management

These utilities provide the foundation for reliable operation
and observability of the DGT Autonomous Movie System.
"""

from .persistence import (
    PersistenceManager, PersistenceMetadata,
    PersistenceManagerFactory
)

from .logger import (
    LoggerManager,
    get_logger_manager, initialize_logging,
    get_game_logger, get_world_logger, get_mind_logger,
    get_body_logger, get_actor_logger, get_narrative_logger,
    get_performance_logger, get_persistence_logger,
    log_performance, log_error_with_context, get_log_stats,
    log_function_calls, log_performance_metrics
)

from .asset_loader import AssetLoader, ObjectRegistry

__all__ = [
    # Persistence
    "PersistenceManager", "PersistenceMetadata", "PersistenceManagerFactory",
    
    # Logger
    "LoggerManager", "get_logger_manager", "initialize_logging",
    "get_game_logger", "get_world_logger", "get_mind_logger",
    "get_body_logger", "get_actor_logger", "get_narrative_logger",
    "get_performance_logger", "get_persistence_logger",
    "log_performance", "log_error_with_context", "get_log_stats",
    "log_function_calls", "log_performance_metrics",
    
    # Asset Loader
    "AssetLoader", "ObjectRegistry"
]
