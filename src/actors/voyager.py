"""
Voyager - The Actor Pillar

Autonomous pathfinding and intent generation with STATE_PONDERING support.
The Voyager navigates the world, discovers Interest Points, and enters
STATE_PONDERING to allow the LLM Chronicler to manifest chaos into narrative.

The Voyager is the bridge between the deterministic world and the chaotic narrative.
"""

import asyncio
import time
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import heapq

from loguru import logger

# Import from core
try:
    from ..core.state import (
        GameState, VoyagerState, MovementIntent, InteractionIntent, PonderIntent,
        InterestPoint, validate_position, DIRECTION_VECTORS
    )
    from ..core.constants import (
        VOYAGER_SPEED_TILES_PER_SECOND, VOYAGER_INTERACTION_RANGE,
        VOYAGER_DISCOVERY_RANGE, VOYAGER_PONDERING_TIMEOUT_SECONDS,
        MOVEMENT_RANGE_TILES, PATHFINDING_MAX_ITERATIONS
    )
except ImportError:
    # Fallback for development
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from core.state import (
        GameState, VoyagerState, MovementIntent, InteractionIntent, PonderIntent,
        InterestPoint, validate_position, DIRECTION_VECTORS
    )
    from core.constants import (
        VOYAGER_SPEED_TILES_PER_SECOND, VOYAGER_INTERACTION_RANGE,
        VOYAGER_DISCOVERY_RANGE, VOYAGER_PONDERING_TIMEOUT_SECONDS,
        MOVEMENT_RANGE_TILES, PATHFINDING_MAX_ITERATIONS
    )


@dataclass
class NavigationGoal:
    """Navigation goal for Voyager"""
    target_position: Tuple[int, int]
    priority: int = 1
    timeout: float = 30.0
    created_at: float = field(default_factory=time.time)
    
    def is_expired(self) -> bool:
        """Check if goal has expired"""
        return time.time() - self.created_at > self.timeout


class PathfindingNode:
    """Node for A* pathfinding algorithm"""
    
    def __init__(self, position: Tuple[int, int], g_cost: float = 0, h_cost: float = 0, parent=None):
        self.position = position
        self.g_cost = g_cost  # Cost from start
        self.h_cost = h_cost  # Heuristic cost to goal
        self.f_cost = g_cost + h_cost  # Total cost
        self.parent = parent
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        return self.position == other.position


class PathfindingNavigator:
    """A* pathfinding and navigation logic"""
    
    def __init__(self, grid_width: int = 50, grid_height: int = 50):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.collision_map = [[False for _ in range(grid_width)] for _ in range(grid_height)]
        
        logger.info(f"🧭 Pathfinding Navigator initialized: {grid_width}x{grid_height}")
    
    async def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                        collision_map: Optional[List[List[bool]]] = None) -> List[Tuple[int, int]]:
        """Find path from start to goal using A* algorithm"""
        if collision_map:
            self.collision_map = collision_map
        
        # A* pathfinding
        path = await self._astar_pathfinding(start, goal, self.collision_map)
        
        if path:
            logger.debug(f"🛤️ Path found: {len(path)} steps from {start} to {goal}")
        else:
            logger.warning(f"❌ No path found from {start} to {goal}")
        
        return path
    
    async def _astar_pathfinding(self, start: Tuple[int, int], goal: Tuple[int, int], 
                                collision_map: List[List[bool]]) -> List[Tuple[int, int]]:
        """A* pathfinding implementation"""
        # Initialize
        open_set = []
        closed_set = set()
        start_node = PathfindingNode(start, 0, self._heuristic(start, goal))
        heapq.heappush(open_set, start_node)
        
        iterations = 0
        
        while open_set and iterations < PATHFINDING_MAX_ITERATIONS:
            iterations += 1
            
            # Get node with lowest f_cost
            current_node = heapq.heappop(open_set)
            closed_set.add(current_node.position)
            
            # Check if we reached goal
            if current_node.position == goal:
                return self._reconstruct_path(current_node)
            
            # Explore neighbors
            for direction, (dx, dy) in DIRECTION_VECTORS.items():
                neighbor_pos = (
                    current_node.position[0] + dx,
                    current_node.position[1] + dy
                )
                
                # Skip if invalid or blocked
                if not self._is_valid_position(neighbor_pos, collision_map):
                    continue
                
                # Skip if already closed
                if neighbor_pos in closed_set:
                    continue
                
                # Calculate costs
                g_cost = current_node.g_cost + 1  # Uniform cost
                h_cost = self._heuristic(neighbor_pos, goal)
                
                neighbor_node = PathfindingNode(neighbor_pos, g_cost, h_cost, current_node)
                
                # Check if neighbor is already in open set with better cost
                existing_node = None
                for node in open_set:
                    if node.position == neighbor_pos:
                        existing_node = node
                        break
                
                if existing_node and existing_node.g_cost <= g_cost:
                    continue
                
                # Add to open set
                heapq.heappush(open_set, neighbor_node)
        
        # No path found
        return []
    
    def _heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Manhattan distance heuristic"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _reconstruct_path(self, end_node: PathfindingNode) -> List[Tuple[int, int]]:
        """Reconstruct path from end node"""
        path = []
        current = end_node
        
        while current:
            path.append(current.position)
            current = current.parent
        
        path.reverse()
        return path
    
    def _is_valid_position(self, position: Tuple[int, int], collision_map: List[List[bool]]) -> bool:
        """Check if position is valid within grid"""
        x, y = position
        
        if y < 0 or y >= len(collision_map):
            return False
        if x < 0 or x >= len(collision_map[0]):
            return False
        
        return not collision_map[y][x]  # False = walkable, True = obstacle
    
    def update_collision_map(self, collision_map: List[List[bool]]) -> None:
        """Update collision map from D&D Engine"""
        self.collision_map = collision_map


class IntentGenerator:
    """Generate intents based on goals and current state"""
    
    def __init__(self, navigator: PathfindingNavigator):
        self.navigator = navigator
        self.current_goals: List[NavigationGoal] = []
        
        logger.info("🎯 Intent Generator initialized")
    
    def add_goal(self, goal: NavigationGoal) -> None:
        """Add navigation goal"""
        self.current_goals.append(goal)
        logger.debug(f"📍 Goal added: {goal.target_position}")
    
    async def generate_movement_intent(self, current_position: Tuple[int, int], 
                                     target_position: Tuple[int, int],
                                     collision_map: Optional[List[List[bool]]] = None) -> MovementIntent:
        """Generate movement intent for target position"""
        # Update collision map if provided
        if collision_map:
            self.navigator.update_collision_map(collision_map)
        
        # Calculate path
        path = await self.navigator.find_path(current_position, target_position)
        
        if not path:
            raise ValueError(f"No path found to {target_position}")
        
        # Calculate confidence based on path quality
        confidence = self._calculate_path_confidence(path)
        
        return MovementIntent(
            target_position=target_position,
            path=path,
            confidence=confidence,
            timestamp=time.time()
        )
    
    def generate_interaction_intent(self, target_entity: str, interaction_type: str,
                                   parameters: Optional[Dict[str, Any]] = None) -> InteractionIntent:
        """Generate interaction intent for entity"""
        return InteractionIntent(
            target_entity=target_entity,
            interaction_type=interaction_type,
            parameters=parameters or {},
            timestamp=time.time()
        )
    
    def get_next_goal(self) -> Optional[NavigationGoal]:
        """Get highest priority active goal"""
        if not self.current_goals:
            return None
        
        # Remove expired goals
        self.current_goals = [goal for goal in self.current_goals if not goal.is_expired()]
        
        if not self.current_goals:
            return None
        
        # Sort by priority (higher first)
        self.current_goals.sort(key=lambda g: g.priority, reverse=True)
        
        return self.current_goals[0]
    
    def _calculate_path_confidence(self, path: List[Tuple[int, int]]) -> float:
        """Calculate confidence score for path"""
        if not path:
            return 0.0
        
        # Base confidence on path length and complexity
        base_confidence = 1.0
        
        # Longer paths have slightly lower confidence
        length_penalty = min(len(path) * 0.01, 0.3)
        
        # Straight paths have higher confidence
        straightness_bonus = self._calculate_path_straightness(path) * 0.2
        
        confidence = base_confidence - length_penalty + straightness_bonus
        return max(0.1, min(1.0, confidence))
    
    def _calculate_path_straightness(self, path: List[Tuple[int, int]]) -> float:
        """Calculate how straight the path is"""
        if len(path) < 2:
            return 1.0
        
        # Calculate total path length
        total_length = len(path)
        
        # Calculate direct distance
        start = path[0]
        end = path[-1]
        direct_distance = abs(end[0] - start[0]) + abs(end[1] - start[1])
        
        # Straightness ratio
        if direct_distance == 0:
            return 1.0
        
        return direct_distance / total_length


class Voyager:
    """Pathfinding and intent generation - The Actor Pillar"""
    
    def __init__(self, dd_engine: DD_Engine):
        self.dd_engine = dd_engine
        self.navigator = PathfindingNavigator()
        self.intent_generator = IntentGenerator(self.navigator)
        
        # Navigation state
        self.current_position: Tuple[int, int] = (10, 25)
        self.last_intent_time: float = 0.0
        self.intent_cooldown: float = 0.01  # Reduced from 0.1s to 0.01s for movie mode
        
        logger.info("🚶 Voyager initialized - Actor Pillar ready")
    
    def update_position(self, new_position: Tuple[int, int]) -> None:
        """Update current position from D&D Engine state"""
        self.current_position = new_position
    
    def generate_movement_intent(self, target: Tuple[int, int]) -> MovementIntent:
        """Generate movement intent for target position"""
        current_state = self.dd_engine.get_current_state()
        collision_map = self.dd_engine.assets.get_collision_map(current_state.current_environment)
        
        return self.intent_generator.generate_movement_intent(
            self.current_position, target, collision_map
        )
    
    def generate_interaction_intent(self, entity: str, interaction_type: str,
                                   parameters: Optional[Dict[str, Any]] = None) -> InteractionIntent:
        """Generate interaction intent for entity"""
        return self.intent_generator.generate_interaction_intent(entity, interaction_type, parameters)
    
    def submit_intent(self, intent: Union[MovementIntent, InteractionIntent]) -> bool:
        """Submit intent to D&D Engine and handle response"""
        # Check intent cooldown
        current_time = time.time()
        if current_time - self.last_intent_time < self.intent_cooldown:
            logger.debug("⏱️ Intent cooldown - waiting")
            return False
        
        self.last_intent_time = current_time
        
        # Validate intent
        validation = self.dd_engine.process_intent(intent)
        
        if not validation.is_valid:
            logger.warning(f"❌ Intent rejected: {validation.validation_result.value} - {validation.message}")
            return False
        
        # Execute intent
        try:
            new_state = self.dd_engine.execute_validated_intent(intent)
            
            # Update internal position
            self.update_position(new_state.player_position)
            
            logger.info(f"✅ Intent executed successfully: {intent.intent_type}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Intent execution failed: {e}")
            return False
    
    def navigate_to_position(self, target_position: Tuple[int, int]) -> bool:
        """Navigate to target position using pathfinding"""
        logger.info(f"🧭 Navigating to {target_position}")
        
        try:
            # Generate movement intent
            intent = self.generate_movement_intent(target_position)
            
            # Submit intent
            success = self.submit_intent(intent)
            
            if success:
                logger.info(f"🎯 Navigation successful: {self.current_position} → {target_position}")
            else:
                logger.warning(f"❌ Navigation failed: {target_position}")
            
            return success
            
        except Exception as e:
            logger.error(f"💥 Navigation error: {e}")
            return False
    
    def interact_with_entity(self, entity: str, interaction_type: str,
                           parameters: Optional[Dict[str, Any]] = None) -> bool:
        """Interact with entity at current position"""
        logger.info(f"🤝 Interacting with {entity}: {interaction_type}")
        
        try:
            # Generate interaction intent
            intent = self.generate_interaction_intent(entity, interaction_type, parameters)
            
            # Submit intent
            success = self.submit_intent(intent)
            
            if success:
                logger.info(f"✅ Interaction successful: {entity}")
            else:
                logger.warning(f"❌ Interaction failed: {entity}")
            
            return success
            
        except Exception as e:
            logger.error(f"💥 Interaction error: {e}")
            return False
    
    def add_navigation_goal(self, target_position: Tuple[int, int], priority: int = 1,
                           timeout: float = 30.0) -> None:
        """Add navigation goal to intent generator"""
        goal = NavigationGoal(
            target_position=target_position,
            priority=priority,
            timeout=timeout
        )
        self.intent_generator.add_goal(goal)
    
    def process_next_goal(self) -> bool:
        """Process the next highest priority goal"""
        goal = self.intent_generator.get_next_goal()
        
        if not goal:
            return False
        
        logger.debug(f"🎯 Processing goal: {goal.target_position}")
        return self.navigate_to_position(goal.target_position)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current Voyager status"""
        current_state = self.dd_engine.get_current_state()
        
        return {
            "position": self.current_position,
            "health": current_state.player_health,
            "environment": current_state.current_environment,
            "active_goals": len(self.intent_generator.current_goals),
            "last_intent_time": self.last_intent_time
        }


# Factory for creating Voyager instances
class VoyagerFactory:
    """Factory for creating Voyager instances"""
    
    @staticmethod
    def create_voyager(dd_engine: DD_Engine) -> Voyager:
        """Create a Voyager with default configuration"""
        return Voyager(dd_engine)
    
    @staticmethod
    def create_test_voyager() -> Voyager:
        """Create a Voyager for testing"""
        from engines.dd_engine import DDEngineFactory
        test_engine = DDEngineFactory.create_test_engine()
        return Voyager(test_engine)
