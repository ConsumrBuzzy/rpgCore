"""
Space Entity - Newtonian Physics Entity

ADR 195: The Newtonian Vector Core

Base entity class for all space objects implementing
the four pillars of "Ur-Asteroids" physics within the
sovereign 160x144 resolution grid.

Entity Types:
- SHIP: Player-controlled triangle with thrust/rotation
- LARGE_ASTEROID: Big rocks that split when hit
- MEDIUM_ASTEROID: Medium rocks from large asteroid splits  
- SMALL_ASTEROID: Small rocks from medium asteroid splits
- BULLET: Player projectiles with limited lifetime
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math
import sys
from pathlib import Path

# Add src to path for absolute imports
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from engines.space.vector2 import Vector2
from dgt_core.kernel.constants import SOVEREIGN_WIDTH, SOVEREIGN_HEIGHT


class EntityType(Enum):
    """Entity types for space physics system"""
    SHIP = "ship"
    LARGE_ASTEROID = "large_asteroid"
    MEDIUM_ASTEROID = "medium_asteroid"
    SMALL_ASTEROID = "small_asteroid"
    BULLET = "bullet"
    SCRAP = "scrap"


@dataclass
class SpaceEntity:
    """Base entity with Newtonian physics properties"""
    
    # Core properties
    entity_type: EntityType
    position: Vector2
    velocity: Vector2
    heading: float  # Angle in radians, 0 = pointing right
    
    # Physical properties
    radius: float
    mass: float = 1.0
    
    # Entity-specific properties
    active: bool = True
    lifetime: Optional[float] = None  # For bullets, in seconds
    age: float = 0.0  # Time since creation, in seconds
    
    # Visual properties
    color: int = 1  # Palette index for rendering
    vertices: List[Vector2] = field(default_factory=list)  # For ship shape
    
    # Physics state
    angular_velocity: float = 0.0  # Rotation speed in rad/s
    thrust_force: float = 0.0  # Current thrust magnitude
    
    def __post_init__(self):
        """Initialize entity-specific properties"""
        if self.entity_type == EntityType.SHIP:
            self._init_ship()
        elif self.entity_type == EntityType.LARGE_ASTEROID:
            self._init_large_asteroid()
        elif self.entity_type == EntityType.MEDIUM_ASTEROID:
            self._init_medium_asteroid()
        elif self.entity_type == EntityType.SMALL_ASTEROID:
            self._init_small_asteroid()
        elif self.entity_type == EntityType.BULLET:
            self._init_bullet()
    
    def _init_ship(self):
        """Initialize ship-specific properties"""
        self.radius = 4.0
        self.mass = 1.0
        self.color = 1  # White
        self.angular_velocity = 0.0
        self.thrust_force = 150.0  # Thrust acceleration
        
        # Triangle shape (pointing right initially)
        self.vertices = [
            Vector2(4, 0),   # Tip
            Vector2(-3, 3),  # Top back
            Vector2(-3, -3)  # Bottom back
        ]
    
    def _init_large_asteroid(self):
        """Initialize large asteroid properties"""
        self.radius = 12.0
        self.mass = 4.0
        self.color = 2  # Gray
        
        # Random initial velocity
        import random
        speed = random.uniform(10, 30)
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = Vector2.from_angle(angle, speed)
        
        # Random angular velocity
        self.angular_velocity = random.uniform(-1, 1)
    
    def _init_medium_asteroid(self):
        """Initialize medium asteroid properties"""
        self.radius = 8.0
        self.mass = 2.0
        self.color = 2  # Gray
        
        # Random initial velocity
        import random
        speed = random.uniform(15, 40)
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = Vector2.from_angle(angle, speed)
        
        # Random angular velocity
        self.angular_velocity = random.uniform(-1.5, 1.5)
    
    def _init_small_asteroid(self):
        """Initialize small asteroid properties"""
        self.radius = 4.0
        self.mass = 1.0
        self.color = 3  # Dark gray
        
        # Random initial velocity
        import random
        speed = random.uniform(20, 50)
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = Vector2.from_angle(angle, speed)
        
        # Random angular velocity
        self.angular_velocity = random.uniform(-2, 2)
    
    def _init_bullet(self):
        """Initialize bullet properties"""
        self.radius = 1.0
        self.mass = 0.1
        self.color = 1  # White
        self.lifetime = 1.0  # 1 second lifetime
        
        # Velocity based on ship heading
        speed = 300.0  # Fast bullet speed
        self.velocity = Vector2.from_angle(self.heading, speed)
    
    def update(self, dt: float) -> None:
        """Update entity physics (60Hz main loop)"""
        if not self.active:
            return
        
        # Update age
        self.age += dt
        
        # Check lifetime (for bullets)
        if self.lifetime is not None and self.age >= self.lifetime:
            self.active = False
            return
        
        # Apply thrust (for ship)
        if self.entity_type == EntityType.SHIP and self.thrust_force > 0:
            thrust_vector = Vector2.from_angle(self.heading, self.thrust_force * dt)
            self.velocity = self.velocity + thrust_vector
        
        # Update position (Newtonian momentum - no friction)
        self.position = self.position + (self.velocity * dt)
        
        # Update heading (for rotating entities)
        if self.angular_velocity != 0:
            self.heading = self.heading + (self.angular_velocity * dt)
            # Normalize heading to [0, 2π]
            self.heading = self.heading % (2 * math.pi)
        
        # Apply toroidal wrap (160x144 boundaries)
        self._apply_toroidal_wrap()
    
    def _apply_toroidal_wrap(self):
        """Apply toroidal screen wrapping at sovereign boundaries"""
        # Wrap X coordinate
        if self.position.x < 0:
            self.position.x = self.position.x + SOVEREIGN_WIDTH
        elif self.position.x >= SOVEREIGN_WIDTH:
            self.position.x = self.position.x - SOVEREIGN_WIDTH
        
        # Wrap Y coordinate  
        if self.position.y < 0:
            self.position.y = self.position.y + SOVEREIGN_HEIGHT
        elif self.position.y >= SOVEREIGN_HEIGHT:
            self.position.y = self.position.y - SOVEREIGN_HEIGHT
    
    def get_wrapped_positions(self) -> List[Vector2]:
        """Get all positions for Newtonian ghosting effect"""
        positions = [self.position]
        
        # Check if near boundaries and add ghost positions
        margin = self.radius + 5  # Ghost margin
        
        # X-axis ghosts
        if self.position.x < margin:
            positions.append(Vector2(self.position.x + SOVEREIGN_WIDTH, self.position.y))
        elif self.position.x > SOVEREIGN_WIDTH - margin:
            positions.append(Vector2(self.position.x - SOVEREIGN_WIDTH, self.position.y))
        
        # Y-axis ghosts
        if self.position.y < margin:
            positions.append(Vector2(self.position.x, self.position.y + SOVEREIGN_HEIGHT))
        elif self.position.y > SOVEREIGN_HEIGHT - margin:
            positions.append(Vector2(self.position.x, self.position.y - SOVEREIGN_HEIGHT))
        
        # Corner ghosts (diagonal)
        if self.position.x < margin and self.position.y < margin:
            positions.append(Vector2(self.position.x + SOVEREIGN_WIDTH, self.position.y + SOVEREIGN_HEIGHT))
        elif self.position.x > SOVEREIGN_WIDTH - margin and self.position.y < margin:
            positions.append(Vector2(self.position.x - SOVEREIGN_WIDTH, self.position.y + SOVEREIGN_HEIGHT))
        elif self.position.x < margin and self.position.y > SOVEREIGN_HEIGHT - margin:
            positions.append(Vector2(self.position.x + SOVEREIGN_WIDTH, self.position.y - SOVEREIGN_HEIGHT))
        elif self.position.x > SOVEREIGN_WIDTH - margin and self.position.y > SOVEREIGN_HEIGHT - margin:
            positions.append(Vector2(self.position.x - SOVEREIGN_WIDTH, self.position.y - SOVEREIGN_HEIGHT))
        
        return positions
    
    def get_world_vertices(self) -> List[Vector2]:
        """Get vertices transformed to world position"""
        if not self.vertices:
            return []
        
        world_vertices = []
        cos_h = math.cos(self.heading)
        sin_h = math.sin(self.heading)
        
        for vertex in self.vertices:
            # Rotate vertex around origin
            rotated_x = vertex.x * cos_h - vertex.y * sin_h
            rotated_y = vertex.x * sin_h + vertex.y * cos_h
            
            # Translate to world position
            world_pos = Vector2(
                rotated_x + self.position.x,
                rotated_y + self.position.y
            )
            world_vertices.append(world_pos)
        
        return world_vertices
    
    def check_collision(self, other: 'SpaceEntity') -> bool:
        """Check circular collision with another entity"""
        if not self.active or not other.active:
            return False
        
        distance = self.position.distance_to(other.position)
        return distance < (self.radius + other.radius)
    
    def split_asteroid(self) -> List['SpaceEntity']:
        """Split asteroid into smaller pieces (entity splitting pillar)"""
        if self.entity_type == EntityType.LARGE_ASTEROID:
            # Create 2 medium asteroids
            return [
                SpaceEntity(
                    entity_type=EntityType.MEDIUM_ASTEROID,
                    position=self.position + Vector2(5, 0),
                    velocity=Vector2.from_angle(0.5, 30),
                    heading=0.0
                ),
                SpaceEntity(
                    entity_type=EntityType.MEDIUM_ASTEROID,
                    position=self.position - Vector2(5, 0),
                    velocity=Vector2.from_angle(-0.5, 30),
                    heading=0.0
                )
            ]
        elif self.entity_type == EntityType.MEDIUM_ASTEROID:
            # Create 2 small asteroids
            return [
                SpaceEntity(
                    entity_type=EntityType.SMALL_ASTEROID,
                    position=self.position + Vector2(3, 0),
                    velocity=Vector2.from_angle(0.8, 40),
                    heading=0.0
                ),
                SpaceEntity(
                    entity_type=EntityType.SMALL_ASTEROID,
                    position=self.position - Vector2(3, 0),
                    velocity=Vector2.from_angle(-0.8, 40),
                    heading=0.0
                )
            ]
        
        return []  # Small asteroids don't split
    
    def apply_thrust(self, thrust_magnitude: float) -> None:
        """Apply thrust force (for ship)"""
        if self.entity_type == EntityType.SHIP:
            self.thrust_force = thrust_magnitude
        else:
            self.thrust_force = 0.0
    
    def rotate(self, angular_velocity: float) -> None:
        """Set angular velocity for rotation"""
        if self.entity_type == EntityType.SHIP:
            self.angular_velocity = angular_velocity
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get entity state for serialization"""
        return {
            'type': self.entity_type.value,
            'position': self.position.to_tuple(),
            'velocity': self.velocity.to_tuple(),
            'heading': self.heading,
            'radius': self.radius,
            'active': self.active,
            'age': self.age
        }
