"""
Race Runner System - Turbo-Scout Bridge

Sprint D: Orchestration Layer - The Turbo Transplant
ADR 215: First Turbo Simulation on Steel Foundation

Implements the Race Runner system skeleton that will serve as the bridge
for the TurboShells migration. This system demonstrates the Plug-and-Play
architecture built in Sprints A-C.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import time
import math
import random

from ...base import BaseSystem, SystemConfig, SystemStatus
from foundation.types import Result
from foundation.protocols import (
    WorldStateSnapshot, EntityStateSnapshot, EntityType, Vector2Protocol
)
from foundation.vector import Vector2
from foundation.registry import DGTRegistry
from .terrain_engine import TerrainEngine


@dataclass
class RaceConfig:
    """Configuration for the race runner system"""
    track_length: float = 1000.0  # Distance to finish
    max_speed: float = 50.0       # Maximum speed
    acceleration: float = 10.0   # Acceleration rate
    deceleration: float = 5.0    # Deceleration rate
    checkpoint_interval: float = 100.0  # Distance between checkpoints
    turbo_boost_multiplier: float = 2.0  # Turbo speed multiplier


@dataclass
class RaceState:
    """State for a single race participant"""
    participant_id: str
    position: Vector2
    velocity: Vector2
    heading: float  # Angle in radians
    distance_traveled: float = 0.0
    checkpoints_passed: int = 0
    current_checkpoint: float = 0.0
    finish_time: Optional[float] = None
    is_turbo_active: bool = False
    turbo_energy: float = 100.0
    position_history: List[Tuple[float, float]] = None
    
    def __post_init__(self):
        if self.position_history is None:
            self.position_history = [(self.position.x, self.position.y)]


class RaceRunnerSystem(BaseSystem):
    """
    Race Runner System - First Turbo Simulation
    
    Implements a simple racing system where participants move across
    a 2D track, demonstrating the BaseSystem orchestration patterns.
    This serves as the foundation for the TurboShells migration.
    """
    
    def __init__(self):
        config = SystemConfig(
            system_id="race_runner",
            system_name="Race Runner System",
            enabled=True,
            debug_mode=False,
            auto_register=True,
            update_interval=1.0 / 60.0,  # 60Hz
            priority=10  # High priority system
        )
        super().__init__(config)
        
        # Race configuration
        self.race_config = RaceConfig()
        
        # Race state
        self.race_active = False
        self.race_start_time: Optional[float] = None
        self.race_finish_time: Optional[float] = None
        self.participants: Dict[str, RaceState] = {}
        
        # Track configuration
        self.track_start = Vector2(50, 72)  # Start position
        self.track_direction = 0.0  # Angle in radians
        self.track_width = 20.0  # Track width
        
        # Terrain engine integration
        self.terrain_engine: Optional[TerrainEngine] = None
        
        # Performance tracking
        self.update_count = 0
        self.last_snapshot_time = 0.0
        self.snapshot_interval = 1.0  # 1 second between snapshots
    
    def _on_initialize(self) -> Result[bool]:
        """Initialize the race runner system"""
        try:
            # Initialize race state
            self._initialize_race_track()
            self._create_default_participants()
            
            self._get_logger().info("🏁 Race Runner System initialized")
            return Result.success_result(True)
            
        except Exception as e:
            return Result.failure_result(f"Race Runner initialization failed: {str(e)}")
    
    def _on_shutdown(self) -> Result[None]:
        """Shutdown the race runner system"""
        try:
            # Stop race if active
            if self.race_active:
                self.stop_race()
            
            # Clear participants
            self.participants.clear()
            
            self._get_logger().info("🏁 Race Runner System shutdown")
            return Result.success_result(None)
            
        except Exception as e:
            return Result.failure_result(f"Race Runner shutdown failed: {str(e)}")
    
    def _on_update(self, dt: float) -> Result[None]:
        """Update the race runner system"""
        try:
            self.update_count += 1
            
            if self.race_active:
                # Update all participants
                self._update_participants(dt)
                
                # Check for race completion
                self._check_race_completion()
                
                # Update registry with race state periodically
                if time.time() - self.last_snapshot_time > self.snapshot_interval:
                    self._update_registry_snapshot()
                    self.last_snapshot_time = time.time()
            
            return Result.success_result(None)
            
        except Exception as e:
            return Result.failure_result(f"Race Runner update failed: {str(e)}")
    
    def _on_handle_event(self, event_type: str, event_data: Dict[str, Any]) -> Result[None]:
        """Handle race runner events"""
        try:
            if event_type == "start_race":
                return self.start_race(event_data.get("participants", []))
            elif event_type == "stop_race":
                return self.stop_race()
            elif event_type == "turbo_boost":
                participant_id = event_data.get("participant_id")
                return self.activate_turbo_boost(participant_id)
            elif event_type == "add_participant":
                participant_id = event_data.get("participant_id")
                position = event_data.get("position", (50, 72))
                return self.add_participant(participant_id, position)
            else:
                return Result.success_result(None)
                
        except Exception as e:
            return Result.failure_result(f"Race Runner event handling failed: {str(e)}")
    
    def _initialize_race_track(self) -> None:
        """Initialize the race track configuration"""
        # Set up a simple straight track
        self.track_start = Vector2(50, 72)
        self.track_direction = 0.0  # Horizontal track
        self.track_width = 20.0
        
        self._get_logger().info(f"🏁 Track initialized: start={self.track_start.to_tuple()}, direction={math.degrees(self.track_direction)}°")
    
    def _create_default_participants(self) -> None:
        """Create default race participants"""
        # Create 3 default participants
        default_positions = [
            ("scout_1", (50, 60)),
            ("scout_2", (50, 72)),  
            ("scout_3", (50, 84))
        ]
        
        for participant_id, position in default_positions:
            self.add_participant(participant_id, position)
    
    def add_participant(self, participant_id: str, position: Tuple[float, float]) -> Result[None]:
        """Add a new participant to the race"""
        try:
            if participant_id in self.participants:
                return Result.failure_result(f"Participant {participant_id} already exists")
            
            # Create participant state
            participant_state = RaceState(
                participant_id=participant_id,
                position=Vector2(position[0], position[1]),
                velocity=Vector2(0, 0),
                heading=0.0
            )
            
            self.participants[participant_id] = participant_state
            
            # Register participant in registry
            registry = DGTRegistry()
            entity_snapshot = EntityStateSnapshot(
                entity_id=participant_id,
                entity_type=EntityType.SHIP,  # Use SHIP type for now
                position=participant_state.position,
                velocity=participant_state.velocity,
                radius=5.0,
                active=True,
                metadata={
                    'system': 'race_runner',
                    'participant_type': 'race_runner',
                    'distance_traveled': 0.0,
                    'checkpoints_passed': 0
                }
            )
            
            registry.register_entity_state(participant_id, entity_snapshot)
            
            self._get_logger().info(f"🏃 Added participant: {participant_id} at {position}")
            return Result.success_result(None)
            
        except Exception as e:
            return Result.failure_result(f"Failed to add participant {participant_id}: {str(e)}")
    
    def start_race(self, participant_ids: Optional[List[str]] = None) -> Result[None]:
        """Start the race"""
        try:
            if self.race_active:
                return Result.failure_result("Race already active")
            
            # Reset race state
            self.race_active = True
            self.race_start_time = time.time()
            self.race_finish_time = None
            
            # Reset participant states
            for participant_id, participant_state in self.participants.items():
                if participant_ids is None or participant_id in participant_ids:
                    participant_state.distance_traveled = 0.0
                    participant_state.checkpoints_passed = 0
                    participant_state.current_checkpoint = 0.0
                    participant_state.finish_time = None
                    participant_state.is_turbo_active = False
                    participant_state.turbo_energy = 100.0
                    participant_state.position_history = [(participant_state.position.x, participant_state.position.y)]
            
            self._get_logger().info("🏁 Race started!")
            return Result.success_result(None)
            
        except Exception as e:
            return Result.failure_result(f"Failed to start race: {str(e)}")
    
    def stop_race(self) -> Result[None]:
        """Stop the race"""
        try:
            if not self.race_active:
                return Result.success_result(None)  # Already stopped
            
            self.race_active = False
            self.race_finish_time = time.time()
            
            self._get_logger().info("🏁 Race stopped!")
            return Result.success_result(None)
            
        except Exception as e:
            return Result.failure_result(f"Failed to stop race: {str(e)}")
    
    def activate_turbo_boost(self, participant_id: str) -> Result[None]:
        """Activate turbo boost for a participant"""
        try:
            if participant_id not in self.participants:
                return Result.failure_result(f"Participant {participant_id} not found")
            
            participant = self.participants[participant_id]
            
            if participant.turbo_energy <= 0:
                return Result.failure_result(f"No turbo energy for {participant_id}")
            
            participant.is_turbo_active = True
            participant.turbo_energy -= 25.0  # Cost per boost
            
            self._get_logger().info(f"🚀 Turbo boost activated for {participant_id}")
            return Result.success_result(None)
            
        except Exception as e:
            return Result.failure_result(f"Failed to activate turbo for {participant_id}: {str(e)}")
    
    def _update_participants(self, dt: float) -> None:
        """Update all participant positions and states"""
        for participant_id, participant in self.participants.items():
            if not self.race_active:
                continue
            
            # Apply physics
            self._update_participant_physics(participant, dt)
            
            # Update position history
            participant.position_history.append((participant.position.x, participant.y))
            
            # Keep history limited
            if len(participant.position_history) > 1000:
                participant.position_history.pop(0)
            
            # Update registry with new position
            self._update_participant_in_registry(participant_id, participant)
    
    def _update_participant_physics(self, participant: RaceState, dt: float) -> None:
        """Update individual participant physics"""
        # Calculate target velocity based on race progress
        target_speed = self.race_config.max_speed
        
        # Apply turbo boost if active
        if participant.is_turbo_active:
            target_speed *= self.race_config.turbo_boost_multiplier
            participant.turbo_energy -= dt * 10.0  # Energy drain
            if participant.turbo_energy <= 0:
                participant.is_turbo_active = False
        
        # Simple acceleration model
        speed_diff = target_speed - participant.velocity.magnitude()
        if speed_diff > 0:
            acceleration = min(self.race_config.acceleration, speed_diff / dt)
        else:
            acceleration = -min(self.race_config.deceleration, -speed_diff / dt)
        
        # Update velocity
        if participant.velocity.magnitude() > 0:
            acceleration_vector = participant.velocity.normalize() * acceleration
        else:
            acceleration_vector = Vector2(math.cos(participant.heading), math.sin(participant.heading)) * acceleration
        
        participant.velocity = participant.velocity + acceleration_vector * dt
        
        # Apply speed limit
        if participant.velocity.magnitude() > target_speed:
            participant.velocity = participant.velocity.normalize() * target_speed
        
        # Update position
        participant.position = participant.position + participant.velocity * dt
        
        # Update distance traveled
        participant.distance_traveled += participant.velocity.magnitude() * dt
        
        # Update checkpoints
        self._update_checkpoints(participant)
    
    def _update_checkpoints(self, participant: RaceState) -> None:
        """Update checkpoint progress for participant"""
        target_checkpoint = (participant.distance_traveled // self.race_config.checkpoint_interval) * self.race_config.checkpoint_interval
        
        if target_checkpoint > participant.current_checkpoint:
            participant.current_checkpoint = target_checkpoint
            participant.checkpoints_passed += 1
            
            self._get_logger().debug(f"🏁 {participant.participant_id} passed checkpoint {participant.checkpoints_passed}")
    
    def _check_race_completion(self) -> None:
        """Check if any participant has finished the race"""
        for participant_id, participant in self.participants.items():
            if participant.distance_traveled >= self.race_config.track_length:
                if participant.finish_time is None:
                    participant.finish_time = time.time()
                    
                    # Announce winner
                    race_time = participant.finish_time - self.race_start_time if self.race_start_time else 0
                    self._get_logger().info(f"🏆 {participant_id} finished race! Time: {race_time:.2f}s")
                    
                    # Stop race
                    self.stop_race()
                    break
    
    def _update_participant_in_registry(self, participant_id: str, participant: RaceState) -> None:
        """Update participant state in registry"""
        try:
            registry = DGTRegistry()
            
            entity_snapshot = EntityStateSnapshot(
                entity_id=participant_id,
                entity_type=EntityType.SHIP,
                position=participant.position,
                velocity=participant.velocity,
                radius=5.0,
                active=True,
                metadata={
                    'system': 'race_runner',
                    'participant_type': 'race_runner',
                    'distance_traveled': participant.distance_traveled,
                    'checkpoints_passed': participant.checkpoints_passed,
                    'is_turbo_active': participant.is_turbo_active,
                    'turbo_energy': participant.turbo_energy,
                    'finish_time': participant.finish_time
                }
            )
            
            registry.register_entity_state(participant_id, entity_snapshot)
            
        except Exception as e:
            self._get_logger().error(f"Failed to update participant in registry: {e}")
    
    def _update_registry_snapshot(self) -> None:
        """Update registry with current race state snapshot"""
        try:
            registry = DGTRegistry()
            
            # Create world snapshot
            entity_snapshots = []
            for participant_id, participant in self.participants.items():
                entity_snapshot = EntityStateSnapshot(
                    entity_id=participant_id,
                    entity_type=EntityType.SHIP,
                    position=participant.position,
                    velocity=participant.velocity,
                    radius=5.0,
                    active=self.race_active,
                    metadata={
                        'system': 'race_runner',
                        'participant_type': 'race_runner',
                        'distance_traveled': participant.distance_traveled,
                        'checkpoints_passed': participant.checkpoints_passed,
                        'is_turbo_active': participant.is_turbo_active,
                        'turbo_energy': participant.turbo_energy,
                        'finish_time': participant.finish_time
                    }
                )
                entity_snapshots.append(entity_snapshot)
            
            # Create world snapshot
            world_snapshot = WorldStateSnapshot(
                timestamp=time.time(),
                frame_count=self.update_count,
                entities=entity_snapshots,
                player_entity_id=None,
                score=0,
                energy=100.0,
                game_active=self.race_active
            )
            
            # Store snapshot in registry metadata
            registry_result = registry.get_world_snapshot()
            if registry_result.success:
                # Store snapshot in system metadata
                self.update_system_metrics("race_runner", {
                    'race_active': self.race_active,
                    'participant_count': len(self.participants),
                    'update_count': self.update_count,
                    'world_snapshot': world_snapshot
                })
            
        except Exception as e:
            self._get_logger().error(f"Failed to update registry snapshot: {e}")
    
    def get_race_state(self) -> Dict[str, Any]:
        """Get current race state"""
        return {
            'race_active': self.race_active,
            'race_start_time': self.race_start_time,
            'race_finish_time': self.race_finish_time,
            'participant_count': len(self.participants),
            'participants': {
                pid: {
                    'position': state.position.to_tuple(),
                    'velocity': state.velocity.to_tuple(),
                    'distance_traveled': state.distance_traveled,
                    'checkpoints_passed': state.checkpoints_passed,
                    'is_turbo_active': state.is_turbo_active,
                    'turbo_energy': state.turbo_energy,
                    'finish_time': state.finish_time
                }
                for pid, state in self.participants.items()
            },
            'track_config': {
                'length': self.race_config.track_length,
                'max_speed': self.race_config.max_speed,
                'checkpoint_interval': self.race_config.checkpoint_interval
            }
        }


# === CONVENIENCE FUNCTIONS ===

def create_race_runner_system() -> RaceRunnerSystem:
    """Create a race runner system instance"""
    return RaceRunnerSystem()


def start_mock_race() -> RaceRunnerSystem:
    """Start a mock race with default participants"""
    system = create_race_runner_system()
    
    # Initialize system
    init_result = system.initialize()
    if not init_result.success:
        raise RuntimeError(f"Failed to initialize race system: {init_result.error}")
    
    # Start race
    start_result = system.handle_event("start_race", {})
    if not start_result.success:
        raise RuntimeError(f"Failed to start race: {start_result.error}")
    
    return system
