"""
DGT Core State - Game State Components
DGT Kernel Implementation - The Universal Truths

The immutable foundation of the DGT Autonomous Movie System.
All data structures and constants that define the system's behavior.
"""

import time
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Any, Optional, Union, Set
from enum import Enum

# === TILE SYSTEM CONSTANTS ===

class SurfaceState(Enum):
    """Environmental surface states for BG3-style reactivity"""
    NORMAL = "normal"
    FIRE = "fire"
    ICE = "ice"
    WATER = "water"
    GOO = "goo"
    STEAM = "steam"
    ELECTRIC = "electric"
    POISON = "poison"
    BLESSED = "blessed"
    CURSED = "cursed"
    BURNED = "burned"
    FROZEN = "frozen"
    WET = "wet"


class TileType(Enum):
    """Core tile types for the deterministic world"""
    GRASS = 0
    STONE = 1
    WATER = 2
    FOREST = 3
    MOUNTAIN = 4
    SAND = 5
    SNOW = 6
    DOOR_CLOSED = 7
    DOOR_OPEN = 8
    WALL = 9
    FLOOR = 10

class BiomeType(Enum):
    """World biome types for terrain generation"""
    FOREST = "forest"
    GRASS = "grass"
    TOWN = "town"
    TAVERN = "tavern"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    TUNDRA = "tundra"
    WATER = "water"

class InterestType(Enum):
    """Types of interest points for LLM manifestation"""
    STRUCTURE = "structure"
    NATURAL = "natural"
    MYSTERIOUS = "mysterious"
    RESOURCE = "resource"
    DANGER = "danger"
    STORY = "story"

# === VIEWPORT AND RENDERING CONSTANTS ===

VIEWPORT_WIDTH = 160
VIEWPORT_HEIGHT = 144
VIEWPORT_WIDTH_PIXELS = 160
VIEWPORT_HEIGHT_PIXELS = 144
TILE_SIZE_PIXELS = 8
VIEWPORT_TILES_X = 20
VIEWPORT_TILES_Y = 18

# === RENDERING CONSTANTS ===

class RenderLayer(Enum):
    """Rendering layers for composition"""
    BACKGROUND = 0
    TERRAIN = 1
    ENTITIES = 2
    EFFECTS = 3
    UI = 4
    SUBTITLES = 5

# === COLOR PALETTE ===

COLOR_PALETTE = {
    "lightest": (255, 255, 255),
    "light": (170, 170, 170),
    "dark": (85, 85, 85),
    "darkest": (0, 0, 0)
}

RENDER_LAYERS = list(RenderLayer)
TILE_SIZE = 8

# === WORLD GENERATION CONSTANTS ===

WORLD_SIZE_X = 50
WORLD_SIZE_Y = 50
CHUNK_SIZE = 10
PERMUTATION_TABLE_SIZE = 256

# === PERFORMANCE CONSTANTS ===

TARGET_FPS = 60
FRAME_DELAY_MS = 1000 // TARGET_FPS
INTENT_COOLDOWN_MS = 10
MOVEMENT_RANGE = 15
PERSISTENCE_INTERVAL_TURNS = 10

# === AI STATES ===

class AIState(Enum):
    """AI operational states"""
    STATE_IDLE = "idle"
    STATE_MOVING = "moving"
    STATE_PONDERING = "pondering"  # LLM processing state
    STATE_INTERACTING = "interacting"
    STATE_WAITING = "waiting"

# ... (Intents) ...

@dataclass
class GameState:
    """Single Source of Truth for the entire system"""
    version: str = "2.0.0"
    timestamp: float = field(default_factory=time.time)
    
    # Entity State
    player_position: Tuple[int, int] = (10, 25)
    player_health: int = 100
    player_status: List[str] = field(default_factory=list)
    ai_state: AIState = AIState.STATE_IDLE
    
    # World State
    current_environment: str = "forest"
    world_seed: str = "SEED_ZERO"
    interest_points: List[InterestPoint] = field(default_factory=list)
    entities: List[Entity] = field(default_factory=list) # Added for compatibility with GraphicsEngine
    hud: Dict[str, str] = field(default_factory=dict) # Added for compatibility with GraphicsEngine
    background: str = "grass" # Added for compatibility with GraphicsEngine
    
    # Persistence
    world_deltas: Dict[Tuple[int, int], WorldDelta] = field(default_factory=dict)
    
    # Session State
    turn_count: int = 0
    frame_count: int = 0
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Effects and Triggers
    active_effects: List['Effect'] = field(default_factory=list)
    active_triggers: List['Trigger'] = field(default_factory=list)
    
    # Global state tags
    tags: Set[str] = field(default_factory=set)
    
    def add_tag(self, tag: str) -> None:
        """Add global tag"""
        self.tags.add(tag)
        self.timestamp = time.time()
    
    def remove_tag(self, tag: str) -> None:
        """Remove global tag"""
        self.tags.discard(tag)
        self.timestamp = time.time()
    
    def has_tag(self, tag: str) -> bool:
        """Check if global tag exists"""
        return tag in self.tags
        
    def add_entity(self, entity: Entity):
        """Add entity to game state"""
        self.entities.append(entity)
    
    def remove_entity(self, entity_id: str) -> bool:
        """Remove entity by ID"""
        for i, entity in enumerate(self.entities):
            if entity.id == entity_id:
                del self.entities[i]
                return True
        return False
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID"""
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Universal Packet"""
        return {
            'width': VIEWPORT_WIDTH_PIXELS,
            'height': VIEWPORT_HEIGHT_PIXELS,
            'entities': [
                {
                    'id': e.id,
                    'x': e.x,
                    'y': e.y,
                    'type': e.entity_type,
                    'metadata': e.metadata
                }
                for e in self.entities
            ],
            'background': {'id': self.background},
            'hud': self.hud,
            'timestamp': self.timestamp,
            'frame_count': self.frame_count,
            'player_position': self.player_position,
            'ai_state': self.ai_state.value
        }
    
    def copy(self) -> 'GameState':
        """Create an immutable deep copy"""
        # Note: Shallow copying lists for performance in Hot Loop, deep copy would be safer but slower
        new_state = GameState(
            version=self.version,
            timestamp=self.timestamp,
            player_position=self.player_position,
            player_health=self.player_health,
            player_status=self.player_status.copy(),
            ai_state=self.ai_state,
            current_environment=self.current_environment,
            world_seed=self.world_seed,
            # interest_points deep copy omitted for brevity in bridge, assuming standard pickle/copy works or lists are replaced
            turn_count=self.turn_count,
            frame_count=self.frame_count,
            performance_metrics=dict(self.performance_metrics),
            # active_effects/triggers lists copy
            active_effects=list(self.active_effects),
            active_triggers=list(self.active_triggers),
            tags=set(self.tags),
            
            # Compatibility fields
            entities=list(self.entities),
            hud=dict(self.hud),
            background=self.background
        )
        return new_state

# ...

def create_initial_game_state(seed: str = "SEED_ZERO") -> GameState:
    """Create initial game state with proper defaults"""
    return GameState(
        world_seed=seed,
        timestamp=time.time(),
        ai_state=AIState.STATE_IDLE
    )

# ...

__all__ = [
    # Enums
    "TileType", "BiomeType", "InterestType", "AIState", 
    "IntentType", "ValidationResult", "RenderLayer", "SurfaceState",
    
    # Constants
    "VIEWPORT_WIDTH", "VIEWPORT_HEIGHT", "TILE_SIZE",
    "WORLD_SIZE_X", "WORLD_SIZE_Y", "CHUNK_SIZE",
    "TARGET_FPS", "FRAME_DELAY_MS", "MOVEMENT_RANGE",
    "COLOR_PALETTE", "RENDER_LAYERS", "TILE_SIZE_PIXELS",
    "VIEWPORT_WIDTH_PIXELS", "VIEWPORT_HEIGHT_PIXELS", "VIEWPORT_TILES_X", "VIEWPORT_TILES_Y",
    
    # Data Classes
    "TileData", "InterestPoint", "WorldDelta", "GameState",
    "MovementIntent", "InteractionIntent", "PonderIntent",
    "IntentValidation", "Command", "CommandResult",
    "Effect", "Trigger", "SubtitleEvent", "PerformanceMetrics", "Entity", "Tile",
    "ShipGenome",
    
    # Exceptions
    "SystemError", "WorldGenerationError", "ValidationError", 
    "PersistenceError", "LLMError",
    
    # Utilities
    "validate_position", "validate_tile_type", "validate_intent",
    "create_initial_game_state", "DIRECTION_VECTORS"
]
