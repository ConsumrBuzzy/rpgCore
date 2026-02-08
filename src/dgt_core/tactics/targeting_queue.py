"""
Targeting Priority Queue - ADR 151 Implementation
Prevents target overkill by managing target assignment across fleet
"""

import heapq
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger


class TargetStatus(Enum):
    """Target engagement status"""
    AVAILABLE = "available"
    ENGAGED = "engaged"
    OVERKILL_RISK = "overkill_risk"
    DESTROYED = "destroyed"


@dataclass
class TargetPriority:
    """Target with priority score for assignment"""
    target_id: str
    position: Tuple[float, float]
    threat_level: float = 1.0  # 0.0 - 1.0
    health_percentage: float = 100.0  # 0.0 - 100.0
    estimated_firepower_needed: float = 50.0
    current_engagers: Set[str] = field(default_factory=set)
    max_recommended_engagers: int = 3
    status: TargetStatus = TargetStatus.AVAILABLE
    last_updated: float = field(default_factory=time.time)
    
    def __lt__(self, other):
        """Heap comparison - higher priority = lower value (min-heap)"""
        return self.priority_score > other.priority_score
    
    @property
    def priority_score(self) -> float:
        """Calculate priority score (higher = more important)"""
        # Base threat priority
        threat_score = self.threat_level * 100
        
        # Health factor (weaker targets get lower priority to prevent overkill)
        health_factor = (self.health_percentage / 100.0) * 50
        
        # Overkill penalty
        overkill_penalty = 0
        if len(self.current_engagers) >= self.max_recommended_engagers:
            overkill_penalty = 200  # Heavy penalty for overkill risk
        
        # Availability bonus
        availability_bonus = 0 if self.status == TargetStatus.AVAILABLE else -100
        
        return threat_score + health_factor + availability_bonus - overkill_penalty
    
    def can_accept_engager(self) -> bool:
        """Check if target can accept another engager"""
        return (self.status == TargetStatus.AVAILABLE and 
                len(self.current_engagers) < self.max_recommended_engagers and
                self.health_percentage > 0.0)
    
    def add_engager(self, ship_id: str) -> bool:
        """Add a ship to engagers list"""
        if self.can_accept_engager():
            self.current_engagers.add(ship_id)
            self._update_status()
            self.last_updated = time.time()
            return True
        return False
    
    def remove_engager(self, ship_id: str):
        """Remove a ship from engagers list"""
        self.current_engagers.discard(ship_id)
        self._update_status()
        self.last_updated = time.time()
    
    def _update_status(self):
        """Update target status based on current state"""
        if self.health_percentage <= 0.0:
            self.status = TargetStatus.DESTROYED
        elif len(self.current_engagers) >= self.max_recommended_engagers:
            self.status = TargetStatus.OVERKILL_RISK
        elif len(self.current_engagers) > 0:
            self.status = TargetStatus.ENGAGED
        else:
            self.status = TargetStatus.AVAILABLE


class TargetingPriorityQueue:
    """Manages target assignment to prevent overkill and optimize fleet effectiveness"""
    
    def __init__(self):
        self.targets: Dict[str, TargetPriority] = {}
        self.priority_heap: List[TargetPriority] = []
        self.ship_assignments: Dict[str, str] = {}  # ship_id -> target_id
        self.max_engagers_per_target = 3
        self.overkill_threshold = 0.8  # 80% of recommended engagers triggers overkill warning
        
        logger.debug("🎯 Targeting Priority Queue initialized")
    
    def add_target(self, target_id: str, position: Tuple[float, float], 
                   threat_level: float = 1.0, health_percentage: float = 100.0,
                   estimated_firepower_needed: float = 50.0) -> bool:
        """Add a new target to the queue"""
        try:
            target = TargetPriority(
                target_id=target_id,
                position=position,
                threat_level=threat_level,
                health_percentage=health_percentage,
                estimated_firepower_needed=estimated_firepower_needed,
                max_recommended_engagers=self.max_engagers_per_target
            )
            
            self.targets[target_id] = target
            heapq.heappush(self.priority_heap, target)
            
            logger.debug(f"🎯 Added target: {target_id} at {position}")
            return True
            
        except Exception as e:
            logger.error(f"🎯 Failed to add target: {e}")
            return False
    
    def remove_target(self, target_id: str) -> bool:
        """Remove a target from the queue"""
        if target_id in self.targets:
            target = self.targets[target_id]
            
            # Remove all engagers
            for ship_id in list(target.current_engagers):
                self.remove_ship_assignment(ship_id)
            
            # Mark as destroyed
            target.status = TargetStatus.DESTROYED
            target.health_percentage = 0.0
            
            logger.debug(f"🎯 Removed target: {target_id}")
            return True
        
        return False
    
    def update_target_health(self, target_id: str, new_health: float) -> bool:
        """Update target health percentage"""
        if target_id not in self.targets:
            return False
        
        target = self.targets[target_id]
        old_health = target.health_percentage
        target.health_percentage = max(0.0, min(100.0, new_health))
        target.last_updated = time.time()
        
        # Update status
        target._update_status()
        
        # Rebuild heap if priority changed significantly
        if abs(old_health - new_health) > 10.0:  # 10% threshold
            self._rebuild_heap()
        
        logger.debug(f"🎯 Updated target health: {target_id} {old_health:.1f}% -> {new_health:.1f}%")
        return True
    
    def assign_ship_to_target(self, ship_id: str, preferred_target_id: Optional[str] = None) -> Optional[str]:
        """Assign a ship to the best available target"""
        # Remove from current assignment if exists
        if ship_id in self.ship_assignments:
            self.remove_ship_assignment(ship_id)
        
        # Try preferred target first
        if preferred_target_id and preferred_target_id in self.targets:
            target = self.targets[preferred_target_id]
            if target.add_engager(ship_id):
                self.ship_assignments[ship_id] = preferred_target_id
                logger.debug(f"🎯 Assigned {ship_id} to preferred target {preferred_target_id}")
                return preferred_target_id
        
        # Find best available target
        best_target = self._find_best_target_for_ship()
        if best_target and best_target.add_engager(ship_id):
            self.ship_assignments[ship_id] = best_target.target_id
            logger.debug(f"🎯 Assigned {ship_id} to best target {best_target.target_id}")
            return best_target.target_id
        
        logger.warning(f"🎯 No available targets for {ship_id}")
        return None
    
    def remove_ship_assignment(self, ship_id: str) -> bool:
        """Remove ship from current target assignment"""
        if ship_id not in self.ship_assignments:
            return False
        
        target_id = self.ship_assignments[ship_id]
        target = self.targets.get(target_id)
        
        if target:
            target.remove_engager(ship_id)
        
        del self.ship_assignments[ship_id]
        logger.debug(f"🎯 Removed assignment: {ship_id} from {target_id}")
        return True
    
    def get_ship_target(self, ship_id: str) -> Optional[str]:
        """Get current target assignment for a ship"""
        return self.ship_assignments.get(ship_id)
    
    def get_target_assignments(self, target_id: str) -> Set[str]:
        """Get all ships assigned to a target"""
        if target_id in self.targets:
            return self.targets[target_id].current_engagers.copy()
        return set()
    
    def get_overkill_risks(self) -> List[str]:
        """Get list of targets at risk of overkill"""
        risky_targets = []
        for target_id, target in self.targets.items():
            if (target.status == TargetStatus.OVERKILL_RISK or 
                len(target.current_engagers) >= self.max_engagers_per_target):
                risky_targets.append(target_id)
        return risky_targets
    
    def redistribute_overkill_targets(self) -> int:
        """Redistribute ships from overkill targets to available targets"""
        redistributed = 0
        overkill_targets = self.get_overkill_risks()
        
        for target_id in overkill_targets:
            target = self.targets[target_id]
            engagers = list(target.current_engagers)
            
            # Remove excess engagers (keep max_recommended)
            excess_count = len(engagers) - target.max_recommended_engagers
            if excess_count > 0:
                for ship_id in engagers[-excess_count:]:
                    self.remove_ship_assignment(ship_id)
                    
                    # Try to reassign to available target
                    new_target = self.assign_ship_to_target(ship_id)
                    if new_target:
                        redistributed += 1
                        logger.debug(f"🎯 Redistributed {ship_id} from {target_id} to {new_target}")
        
        if redistributed > 0:
            logger.info(f"🎯 Redistributed {redistributed} ships from overkill targets")
        
        return redistributed
    
    def get_targeting_summary(self) -> Dict[str, Any]:
        """Get comprehensive targeting summary"""
        total_targets = len(self.targets)
        available_targets = sum(1 for t in self.targets.values() if t.status == TargetStatus.AVAILABLE)
        engaged_targets = sum(1 for t in self.targets.values() if t.status == TargetStatus.ENGAGED)
        overkill_risks = len(self.get_overkill_risks())
        
        return {
            "total_targets": total_targets,
            "available_targets": available_targets,
            "engaged_targets": engaged_targets,
            "overkill_risks": overkill_risks,
            "assigned_ships": len(self.ship_assignments),
            "unassigned_ships": len(self.ship_assignments) - len(set(self.ship_assignments.values())),
            "efficiency_score": (available_targets + engaged_targets) / max(total_targets, 1)
        }
    
    def _find_best_target_for_ship(self) -> Optional[TargetPriority]:
        """Find the best available target for assignment"""
        # Clean up the heap first
        self._cleanup_heap()
        
        # Find first available target
        while self.priority_heap:
            target = heapq.heappop(self.priority_heap)
            
            # Check if target is still valid and available
            if (target.target_id in self.targets and 
                self.targets[target.target_id] == target and
                target.can_accept_engager()):
                
                # Put it back for others
                heapq.heappush(self.priority_heap, target)
                return target
        
        return None
    
    def _cleanup_heap(self):
        """Remove invalid targets from heap"""
        valid_targets = []
        current_time = time.time()
        
        while self.priority_heap:
            target = heapq.heappop(self.priority_heap)
            
            # Check if target is still valid
            if (target.target_id in self.targets and 
                self.targets[target.target_id] == target and
                target.status != TargetStatus.DESTROYED):
                
                # Update stale targets
                if current_time - target.last_updated > 30.0:  # 30 second timeout
                    target._update_status()
                
                valid_targets.append(target)
        
        # Rebuild heap with valid targets
        self.priority_heap = valid_targets
        heapq.heapify(self.priority_heap)
    
    def _rebuild_heap(self):
        """Rebuild the priority heap from current targets"""
        self.priority_heap = list(self.targets.values())
        heapq.heapify(self.priority_heap)
    
    def clear_all_assignments(self):
        """Clear all ship assignments"""
        for ship_id in list(self.ship_assignments.keys()):
            self.remove_ship_assignment(ship_id)
        
        for target in self.targets.values():
            target.current_engagers.clear()
            target._update_status()
        
        logger.info("🎯 Cleared all target assignments")


# Global targeting queue instance
targeting_queue = TargetingPriorityQueue()
