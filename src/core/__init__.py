"""
Core Module - Foundation of the DGT Autonomous Movie System

This module provides the foundational components that all other modules depend on:
- state.py: Immutable data structures and system state
- heartbeat.py: 60 FPS asynchronous main loop
- constants.py: System configuration and magic numbers

The core follows SOLID principles and provides a stable foundation for the
Four-Pillar Architecture (World, Mind, Body, Actor) and Narrative systems.
"""

from .state import (
    # Enums
    TileType, BiomeType, InterestType, VoyagerState, IntentType, ValidationResult,
    
    # Constants
    VIEWPORT_WIDTH, VIEWPORT_HEIGHT, TILE_SIZE, WORLD_SIZE_X, WORLD_SIZE_Y,
    TARGET_FPS, FRAME_DELAY_MS, MOVEMENT_RANGE,
    
    # Core Data Classes
    TileData, InterestPoint, WorldDelta, GameState,
    MovementIntent, InteractionIntent, PonderIntent,
    IntentValidation, Command, CommandResult,
    Effect, Trigger, SubtitleEvent, PerformanceMetrics,
    
    # Exceptions
    SystemError, WorldGenerationError, ValidationError, PersistenceError, LLMError,
    
    # Utilities
    validate_position, validate_tile_type, validate_intent,
    create_initial_game_state, DIRECTION_VECTORS
)

from .heartbeat import (
    HeartbeatController, HeartbeatMetrics,
    get_heartbeat, initialize_heartbeat
)

from .constants import (
    # System identification
    SYSTEM_NAME, SYSTEM_VERSION, SYSTEM_ARCHITECTURE, SYSTEM_TARGET,
    
    # World generation
    WORLD_SEED_DEFAULT, WORLD_SIZE_X, WORLD_SIZE_Y, CHUNK_SIZE,
    INTEREST_POINT_DENSITY, NOISE_SCALE, NOISE_OCTAVES,
    
    # Rendering
    TILE_SIZE_PIXELS, VIEWPORT_WIDTH_PIXELS, VIEWPORT_HEIGHT_PIXELS,
    RENDER_LAYERS, COLOR_PALETTE,
    
    # Performance
    TARGET_FPS, FRAME_DELAY_MS, INTENT_COOLDOWN_MS, MOVEMENT_RANGE_TILES,
    
    # Voyager
    VOYAGER_SPEED_TILES_PER_SECOND, VOYAGER_DISCOVERY_RANGE,
    
    # Persistence
    PERSISTENCE_FORMAT, PERSISTENCE_INTERVAL_TURNS, PERSISTENCE_FILE,
    
    # LLM
    LLM_PROVIDER, LLM_MODEL, LLM_TIMEOUT_SECONDS,
    SUBTITLE_DEFAULT_DURATION, SUBTITLE_POSITION_Y,
    
    # System utilities
    get_environment, is_development, is_production, is_debug_mode,
    get_project_root, get_config_path, get_assets_path,
    get_system_config, initialize_constants
)

__version__ = "2.0.0"
__all__ = [
    # From state module
    "TileType", "BiomeType", "InterestType", "VoyagerState", "IntentType", "ValidationResult",
    "VIEWPORT_WIDTH", "VIEWPORT_HEIGHT", "TILE_SIZE", "WORLD_SIZE_X", "WORLD_SIZE_Y",
    "TARGET_FPS", "FRAME_DELAY_MS", "MOVEMENT_RANGE",
    "TileData", "InterestPoint", "WorldDelta", "GameState",
    "MovementIntent", "InteractionIntent", "PonderIntent",
    "IntentValidation", "Command", "CommandResult",
    "Effect", "Trigger", "SubtitleEvent", "PerformanceMetrics",
    "SystemError", "WorldGenerationError", "ValidationError", "PersistenceError", "LLMError",
    "validate_position", "validate_tile_type", "validate_intent",
    "create_initial_game_state", "DIRECTION_VECTORS",
    
    # From heartbeat module
    "HeartbeatController", "HeartbeatMetrics",
    "get_heartbeat", "initialize_heartbeat",
    
    # From constants module
    "SYSTEM_NAME", "SYSTEM_VERSION", "SYSTEM_ARCHITECTURE", "SYSTEM_TARGET",
    "WORLD_SEED_DEFAULT", "CHUNK_SIZE", "INTEREST_POINT_DENSITY", "NOISE_SCALE",
    "TILE_SIZE_PIXELS", "VIEWPORT_WIDTH_PIXELS", "VIEWPORT_HEIGHT_PIXELS",
    "RENDER_LAYERS", "COLOR_PALETTE",
    "FRAME_DELAY_MS", "INTENT_COOLDOWN_MS", "MOVEMENT_RANGE_TILES",
    "VOYAGER_SPEED_TILES_PER_SECOND", "VOYAGER_DISCOVERY_RANGE",
    "PERSISTENCE_FORMAT", "PERSISTENCE_INTERVAL_TURNS", "PERSISTENCE_FILE",
    "LLM_PROVIDER", "LLM_MODEL", "LLM_TIMEOUT_SECONDS",
    "SUBTITLE_DEFAULT_DURATION", "SUBTITLE_POSITION_Y",
    "get_environment", "is_development", "is_production", "is_debug_mode",
    "get_project_root", "get_config_path", "get_assets_path",
    "get_system_config", "initialize_constants"
]
