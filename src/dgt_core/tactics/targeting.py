"""
Tactical Targeting System - Pure Math-Driven Target Assignment
ADR 151: KISS Targeting with DPS vs Armor Escalation Logic
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import time

from loguru import logger


@dataclass
class TacticalTarget:
    """Pure math-driven target representation"""
    ship_id: str
    position: Tuple[float, float]
    armor: float
    current_health: float
    max_health: float
    threat_level: float = 1.0
    priority: float = 1.0
    assigned_count: int = 0
    last_assigned: float = 0.0
    
    def __post_init__(self):
        if self.priority == 1.0:
            self.priority = self._calculate_priority()
    
    def _calculate_priority(self) -> float:
        """Calculate priority based on threat and health"""
        health_factor = self.current_health / self.max_health
        return self.threat_level * (2.0 - health_factor)  # Higher priority for damaged high-threat targets


class TargetingPriorityQueue:
    """Pure Math-driven targeting. Escalates based on DPS vs Armor."""
    
    def __init__(self, max_engagers: int = 3):
        self.targets: Dict[str, TacticalTarget] = {}
        self.max_engagers = max_engagers
        self.ship_assignments: Dict[str, str] = {}  # ship_id -> target_id
        self.fleet_dps: float = 0.0
        
        logger.debug(f"🎯 Tactical Targeting initialized: max_engagers={max_engagers}")
    
    def update_fleet_dps(self, fleet_dps: float):
        """Update fleet DPS for escalation calculations"""
        self.fleet_dps = fleet_dps
        logger.debug(f"🎯 Fleet DPS updated: {fleet_dps:.1f}")
    
    def add_target(self, ship_id: str, position: Tuple[float, float], 
                   armor: float, current_health: float, max_health: float,
                   threat_level: float = 1.0) -> bool:
        """Add or update a target"""
        try:
            target = TacticalTarget(
                ship_id=ship_id,
                position=position,
                armor=armor,
                current_health=current_health,
                max_health=max_health,
                threat_level=threat_level
            )
            
            self.targets[ship_id] = target
            logger.debug(f"🎯 Added target: {ship_id} (armor={armor}, health={current_health}/{max_health})")
            return True
            
        except Exception as e:
            logger.error(f"🎯 Failed to add target: {e}")
            return False
    
    def assign_ship(self, ship_id: str, preferred_target: Optional[str] = None) -> Optional[str]:
        """Assign ship to optimal target using pure math"""
        # Remove from current assignment if exists
        if ship_id in self.ship_assignments:
            self._remove_assignment(ship_id)
        
        # Try preferred target first
        if preferred_target and preferred_target in self.targets:
            if self._can_assign_to_target(preferred_target):
                self._make_assignment(ship_id, preferred_target)
                return preferred_target
        
        # Find optimal target using numpy for vector math
        best_target = self._find_optimal_target()
        if best_target:
            self._make_assignment(ship_id, best_target)
            return best_target
        
        return None
    
    def _can_assign_to_target(self, target_id: str) -> bool:
        """Check if ship can be assigned to target"""
        if target_id not in self.targets:
            return False
        
        target = self.targets[target_id]
        
        # Skip destroyed targets
        if target.current_health <= 0:
            return False
        
        # Calculate dynamic limit based on DPS vs Armor
        dynamic_limit = self._calculate_dynamic_limit(target)
        
        return target.assigned_count < dynamic_limit
    
    def _calculate_dynamic_limit(self, target: TacticalTarget) -> int:
        """
        Escalation Logic: If fleet DPS < target armor, 
        override the 3-ship limit to prevent stalemate.
        """
        base_limit = self.max_engagers
        
        # Systemic Fix: Prevent infinite kiting loops
        if self.fleet_dps > 0:
            dps_armor_ratio = self.fleet_dps / target.armor
            
            # Escalate if we can't break through armor quickly
            if dps_armor_ratio < 0.67:  # Fleet DPS is less than 2/3 of target armor
                return base_limit + 2
            elif dps_armor_ratio < 1.0:  # Fleet DPS is less than armor
                return base_limit + 1
        
        return base_limit
    
    def _find_optimal_target(self) -> Optional[str]:
        """Find optimal target using numpy vector math"""
        if not self.targets:
            return None
        
        # Filter available targets
        available_targets = [
            (tid, target) for tid, target in self.targets.items()
            if self._can_assign_to_target(tid)
        ]
        
        if not available_targets:
            return None
        
        # Calculate priority scores using numpy
        target_ids = [tid for tid, _ in available_targets]
        priorities = np.array([target.priority for _, target in available_targets])
        
        # Add distance factor if we have ship positions (simplified for now)
        # In full implementation, would use actual ship positions
        distance_factors = np.ones(len(target_ids))  # Placeholder
        
        # Combined score (higher is better)
        scores = priorities * distance_factors
        
        # Select best target
        best_idx = np.argmax(scores)
        return target_ids[best_idx]
    
    def _make_assignment(self, ship_id: str, target_id: str):
        """Make ship assignment"""
        self.ship_assignments[ship_id] = target_id
        self.targets[target_id].assigned_count += 1
        self.targets[target_id].last_assigned = time.time()
        
        logger.debug(f"🎯 Assigned {ship_id} -> {target_id}")
    
    def _remove_assignment(self, ship_id: str):
        """Remove ship assignment"""
        if ship_id in self.ship_assignments:
            target_id = self.ship_assignments[ship_id]
            if target_id in self.targets:
                self.targets[target_id].assigned_count = max(0, self.targets[target_id].assigned_count - 1)
            del self.ship_assignments[ship_id]
    
    def update_target_health(self, target_id: str, new_health: float) -> bool:
        """Update target health"""
        if target_id not in self.targets:
            return False
        
        target = self.targets[target_id]
        target.current_health = max(0.0, new_health)
        target.priority = target._calculate_priority()
        
        logger.debug(f"🎯 Updated health: {target_id} -> {new_health:.1f}")
        return True
    
    def remove_target(self, target_id: str) -> bool:
        """Remove target from queue"""
        if target_id in self.targets:
            # Remove all assignments to this target
            assigned_ships = [
                ship_id for ship_id, assigned_target in self.ship_assignments.items()
                if assigned_target == target_id
            ]
            
            for ship_id in assigned_ships:
                self._remove_assignment(ship_id)
            
            del self.targets[target_id]
            logger.debug(f"🎯 Removed target: {target_id}")
            return True
        
        return False
    
    def get_targeting_summary(self) -> Dict[str, any]:
        """Get targeting summary for monitoring"""
        total_targets = len(self.targets)
        active_targets = sum(1 for t in self.targets.values() if t.current_health > 0)
        total_assignments = len(self.ship_assignments)
        
        return {
            "total_targets": total_targets,
            "active_targets": active_targets,
            "total_assignments": total_assignments,
            "fleet_dps": self.fleet_dps,
            "max_engagers": self.max_engagers,
            "efficiency": total_assignments / max(active_targets, 1)
        }
    
    def clear_all_assignments(self):
        """Clear all assignments"""
        self.ship_assignments.clear()
        for target in self.targets.values():
            target.assigned_count = 0
        
        logger.info("🎯 Cleared all targeting assignments")


# Global tactical targeting instance
tactical_targeting = TargetingPriorityQueue()
