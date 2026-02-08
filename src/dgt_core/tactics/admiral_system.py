from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
import math

from src.dgt_core.simulation.space_physics import SpaceShip

class FleetOrder(Enum):
    """Tactical orders for the fleet"""
    FREE_ENGAGE = auto() # Default: pilots choose targets
    FOCUS_FIRE = auto()  # All ships attack specific target
    RALLY = auto()       # All ships move to rally point
    DEFEND = auto()      # Protect a specific VIP

class Admiral:
    """Tactical Layer Analysis Engine"""
    
    def __init__(self, fleet_id: str):
        self.fleet_id = fleet_id
        self.current_order: FleetOrder = FleetOrder.FREE_ENGAGE
        self.focus_target_id: Optional[str] = None
        self.rally_point: Optional[Tuple[float, float]] = None
    
    def issue_order(self, order: FleetOrder, target_id: Optional[str] = None, point: Optional[Tuple[float, float]] = None):
        """Issue a new fleet-wide order"""
        self.current_order = order
        self.focus_target_id = target_id
        self.rally_point = point
        
    def calculate_fleet_center(self, ships: List[SpaceShip]) -> Tuple[float, float]:
        """Calculate the centroid of the fleet"""
        if not ships:
            return (0.0, 0.0)
        
        avg_x = sum(s.x for s in ships) / len(ships)
        avg_y = sum(s.y for s in ships) / len(ships)
        return (avg_x, avg_y)

    def get_tactical_inputs(self, ship: SpaceShip, fleet_center: Tuple[float, float], target_map: Dict[str, SpaceShip]) -> Dict[str, float]:
        """
        Calculate NEAT inputs for the "Admiral" layer.
        Returns normalized vectors (-1.0 to 1.0).
        """
        inputs = {}
        
        # 1. Vector to Fleet Center (Formation Keeping)
        dx_center = fleet_center[0] - ship.x
        dy_center = fleet_center[1] - ship.y
        dist_center = math.sqrt(dx_center**2 + dy_center**2) + 0.001
        inputs['vec_fleet_center_x'] = dx_center / dist_center
        inputs['vec_fleet_center_y'] = dy_center / dist_center
        
        # 2. Vector to Focus Target (Admiral's Command)
        if self.current_order == FleetOrder.FOCUS_FIRE and self.focus_target_id:
            target = target_map.get(self.focus_target_id)
            if target:
                dx_target = target.x - ship.x
                dy_target = target.y - ship.y
                dist_target = math.sqrt(dx_target**2 + dy_target**2) + 0.001
                inputs['vec_focus_target_x'] = dx_target / dist_target
                inputs['vec_focus_target_y'] = dy_target / dist_target
            else:
                # Target lost/destroyed -> Fallback to 0
                inputs['vec_focus_target_x'] = 0.0
                inputs['vec_focus_target_y'] = 0.0
        else:
            inputs['vec_focus_target_x'] = 0.0
            inputs['vec_focus_target_y'] = 0.0
            
        return inputs
