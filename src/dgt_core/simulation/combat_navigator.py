"""
DGT Combat Navigator - ADR 130 Implementation
AI combat system with intent switching and tactical decision-making

Replaces simple pathfinding with combat-aware navigation
Supports pursuit, strafing, retreat, and evasion tactics
"""

import math
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel, Field
from loguru import logger

from .space_physics import SpaceShip, CombatIntent, SpaceVoyagerEngine, TargetingSystem


class TacticalSituation(str, Enum):
    """Tactical situation assessment"""
    ADVANTAGE = "advantage"           # We have the advantage
    DISADVANTAGE = "disadvantage"     # We are at disadvantage
    NEUTRAL = "neutral"               # Even match
    OVERWHELMED = "overwhelmed"       # Outmatched
    VICTORY = "victory"               # Enemy nearly defeated


class ManeuverType(str, Enum):
    """Combat maneuver types"""
    HEAD_ON_ATTACK = "head_on_attack"
    FLANKING_ATTACK = "flanking_attack"
    BROADSIDE_STRAFE = "broadside_strafe"
    DEFENSIVE_EVADE = "defensive_evade"
    TACTICAL_RETREAT = "tactical_retreat"
    CIRCLE_OF_DEATH = "circle_of_death"  # Death spiral maneuver


@dataclass
class TacticalPosition:
    """Tactical position assessment"""
    distance_to_target: float
    angle_to_target: float
    relative_velocity: float
    target_heading: float
    advantage_score: float
    threat_level: float
    
    def is_optimal_range(self, optimal_range: float, tolerance: float = 50.0) -> bool:
        """Check if within optimal weapon range"""
        return abs(self.distance_to_target - optimal_range) <= tolerance
    
    def is_flanking_position(self, flank_angle: float = 90.0) -> bool:
        """Check if in flanking position"""
        return abs(self.angle_to_target) >= flank_angle
    
    def is_dangerous_close(self, danger_distance: float = 50.0) -> bool:
        """Check if dangerously close to target"""
        return self.distance_to_target < danger_distance


class CombatNavigator:
    """AI combat navigator with intent switching and tactical awareness"""
    
    def __init__(self, ship: SpaceShip, targeting_system: TargetingSystem):
        self.ship = ship
        self.targeting_system = targeting_system
        
        # Combat AI parameters
        self.aggression_level = 0.7  # 0.0 = defensive, 1.0 = aggressive
        self.tactical_skill = 0.8    # Affects decision quality
        self.risk_tolerance = 0.6    # Willingness to take risks
        
        # Intent switching
        self.current_intent = CombatIntent.PURSUIT
        self.intent_switch_cooldown = 0.0
        self.intent_persistence = 2.0  # Minimum time before switching
        
        # Tactical memory
        self.last_target_position: Optional[Tuple[float, float]] = None
        self.target_velocity_history: List[Tuple[float, float]] = []
        self.combat_history: List[Dict[str, Any]] = []
        
        # Maneuver parameters
        self.preferred_combat_range = 150.0
        self.minimum_safe_distance = 80.0
        self.maximum_engagement_range = 300.0
        
        logger.debug(f"🚀 CombatNavigator initialized for {ship.ship_id}")
    
    def update(self, all_ships: List[SpaceShip], current_time: float, dt: float) -> Dict[str, Any]:
        """Update combat navigation and tactical decisions"""
        navigation_data = {
            'intent': self.current_intent,
            'target_id': None,
            'target_position': None,
            'maneuver': None,
            'tactical_situation': TacticalSituation.NEUTRAL,
            'should_fire': False,
            'reasoning': []
        }
        
        # Update intent cooldown
        if self.intent_switch_cooldown > 0:
            self.intent_switch_cooldown -= dt
        
        # Find target
        target = self.targeting_system.find_nearest_enemy(self.ship, all_ships)
        if target:
            navigation_data['target_id'] = target.ship_id
            navigation_data['target_position'] = (target.x, target.y)
            
            # Assess tactical situation
            tactical_pos = self._assess_tactical_position(target)
            situation = self._assess_tactical_situation(target, tactical_pos)
            navigation_data['tactical_situation'] = situation
            
            # Update target tracking
            self._update_target_tracking(target, current_time)
            
            # Determine combat intent
            new_intent = self._determine_combat_intent(situation, tactical_pos, current_time)
            if new_intent != self.current_intent and self.intent_switch_cooldown <= 0:
                self.current_intent = new_intent
                self.intent_switch_cooldown = self.intent_persistence
                navigation_data['reasoning'].append(f"Intent switched to {new_intent.value}")
            
            # Execute tactical maneuver
            maneuver_data = self._execute_tactical_maneuver(target, tactical_pos, dt)
            navigation_data.update(maneuver_data)
            
            # Combat decision
            navigation_data['should_fire'] = self._should_fire_weapon(target, tactical_pos, current_time)
        
        return navigation_data
    
    def _assess_tactical_position(self, target: SpaceShip) -> TacticalPosition:
        """Assess current tactical position relative to target"""
        dx = target.x - self.ship.x
        dy = target.y - self.ship.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Calculate angle to target relative to ship heading
        angle_to_target = math.degrees(math.atan2(dy, dx))
        relative_angle = (angle_to_target - self.ship.heading + 180) % 360 - 180
        
        # Calculate relative velocity
        rel_vx = target.velocity_x - self.ship.velocity_x
        rel_vy = target.velocity_y - self.ship.velocity_y
        relative_velocity = math.sqrt(rel_vx**2 + rel_vy**2)
        
        # Calculate advantage score
        advantage_score = self._calculate_advantage_score(target, distance, relative_velocity)
        
        # Calculate threat level
        threat_level = self._calculate_threat_level(target, distance, relative_velocity)
        
        return TacticalPosition(
            distance_to_target=distance,
            angle_to_target=relative_angle,
            relative_velocity=relative_velocity,
            target_heading=target.heading,
            advantage_score=advantage_score,
            threat_level=threat_level
        )
    
    def _calculate_advantage_score(self, target: SpaceShip, distance: float, rel_velocity: float) -> float:
        """Calculate tactical advantage score"""
        score = 0.0
        
        # Hull integrity advantage
        hull_advantage = (self.ship.hull_integrity - target.hull_integrity) / 100.0
        score += hull_advantage * 0.3
        
        # Shield advantage
        shield_advantage = (self.ship.shield_strength - target.shield_strength) / 100.0
        score += shield_advantage * 0.2
        
        # Position advantage (being at optimal range)
        if distance <= self.ship.weapon_range:
            score += 0.3
        
        # Speed advantage
        speed_diff = self.ship.get_speed() - target.get_speed()
        score += (speed_diff / 10.0) * 0.2
        
        return max(-1.0, min(1.0, score))
    
    def _calculate_threat_level(self, target: SpaceShip, distance: float, rel_velocity: float) -> float:
        """Calculate threat level from target"""
        threat = 0.0
        
        # Proximity threat
        if distance < self.minimum_safe_distance:
            threat += (self.minimum_safe_distance - distance) / self.minimum_safe_distance
        
        # Weapon threat
        if distance <= target.weapon_range:
            threat += 0.5
        
        # Speed threat (fast closing targets)
        if rel_velocity > 5.0:
            threat += 0.3
        
        return max(0.0, min(1.0, threat))
    
    def _assess_tactical_situation(self, target: SpaceShip, tactical_pos: TacticalPosition) -> TacticalSituation:
        """Assess overall tactical situation"""
        if target.hull_integrity < 20.0:
            return TacticalSituation.VICTORY
        elif tactical_pos.advantage_score > 0.5:
            return TacticalSituation.ADVANTAGE
        elif tactical_pos.advantage_score < -0.5:
            return TacticalSituation.DISADVANTAGE
        elif tactical_pos.threat_level > 0.7:
            return TacticalSituation.OVERWHELMED
        else:
            return TacticalSituation.NEUTRAL
    
    def _determine_combat_intent(self, situation: TacticalSituation, tactical_pos: TacticalPosition, current_time: float) -> CombatIntent:
        """Determine combat intent based on tactical assessment"""
        
        # Victory situation - press the attack
        if situation == TacticalSituation.VICTORY:
            return CombatIntent.PURSUIT
        
        # Advantage situation - based on aggression
        elif situation == TacticalSituation.ADVANTAGE:
            if self.aggression_level > 0.7:
                return CombatIntent.PURSUIT
            elif tactical_pos.is_optimal_range(self.preferred_combat_range):
                return CombatIntent.STRAFE
            else:
                return CombatIntent.PURSUIT
        
        # Disadvantage situation - tactical response
        elif situation == TacticalSituation.DISADVANTAGE:
            if tactical_pos.threat_level > 0.6:
                return CombatIntent.EVADE
            elif self.ship.hull_integrity < 40.0:
                return CombatIntent.RETREAT
            else:
                return CombatIntent.STRAFE
        
        # Overwhelmed situation - defensive
        elif situation == TacticalSituation.OVERWHELMED:
            if self.ship.hull_integrity < 30.0:
                return CombatIntent.RETREAT
            else:
                return CombatIntent.EVADE
        
        # Neutral situation - balanced approach
        else:
            if tactical_pos.distance_to_target > self.preferred_combat_range + 50:
                return CombatIntent.PURSUIT
            elif tactical_pos.is_dangerous_close(self.minimum_safe_distance):
                return CombatIntent.EVADE
            else:
                return CombatIntent.STRAFE
    
    def _execute_tactical_maneuver(self, target: SpaceShip, tactical_pos: TacticalPosition, dt: float) -> Dict[str, Any]:
        """Execute tactical maneuver based on current intent"""
        maneuver_data = {
            'maneuver': None,
            'target_position': (target.x, target.y),
            'maneuver_description': []
        }
        
        if self.current_intent == CombatIntent.PURSUIT:
            maneuver = self._execute_pursuit_maneuver(target, tactical_pos, dt)
        elif self.current_intent == CombatIntent.STRAFE:
            maneuver = self._execute_strafe_maneuver(target, tactical_pos, dt)
        elif self.current_intent == CombatIntent.EVADE:
            maneuver = self._execute_evasion_maneuver(target, tactical_pos, dt)
        elif self.current_intent == CombatIntent.RETREAT:
            maneuver = self._execute_retreat_maneuver(target, tactical_pos, dt)
        else:  # LOCKED
            maneuver = self._execute_locked_maneuver(target, tactical_pos, dt)
        
        maneuver_data.update(maneuver)
        return maneuver_data
    
    def _execute_pursuit_maneuver(self, target: SpaceShip, tactical_pos: TacticalPosition, dt: float) -> Dict[str, Any]:
        """Execute aggressive pursuit maneuver"""
        # Predict target position based on velocity
        predicted_x = target.x + target.velocity_x * 0.5  # 0.5 second prediction
        predicted_y = target.y + target.velocity_y * 0.5
        
        # Check for head-on vs flanking approach
        if tactical_pos.distance_to_target > self.preferred_combat_range:
            # Long range - direct approach
            maneuver_type = ManeuverType.HEAD_ON_ATTACK
            description = "Direct approach to engage"
        else:
            # Medium range - consider flanking
            if abs(tactical_pos.angle_to_target) > 45:
                maneuver_type = ManeuverType.FLANKING_ATTACK
                description = "Flanking attack from angle"
            else:
                maneuver_type = ManeuverType.HEAD_ON_ATTACK
                description = "Head-on attack"
        
        return {
            'maneuver': maneuver_type,
            'target_position': (predicted_x, predicted_y),
            'maneuver_description': [description]
        }
    
    def _execute_strafe_maneuver(self, target: SpaceShip, tactical_pos: TacticalPosition, dt: float) -> Dict[str, Any]:
        """Execute broadside strafing maneuver"""
        # Calculate perpendicular strafing position
        angle_to_target_rad = math.radians(math.degrees(math.atan2(
            target.y - self.ship.y, 
            target.x - self.ship.x
        )) + 90)  # Perpendicular angle
        
        # Maintain optimal range with lateral movement
        strafe_distance = self.preferred_combat_range
        strafe_x = target.x + math.cos(angle_to_target_rad) * strafe_distance
        strafe_y = target.y + math.sin(angle_to_target_rad) * strafe_distance
        
        return {
            'maneuver': ManeuverType.BROADSIDE_STRAFE,
            'target_position': (strafe_x, strafe_y),
            'maneuver_description': ["Broadside strafing at optimal range"]
        }
    
    def _execute_evasion_maneuver(self, target: SpaceShip, tactical_pos: TacticalPosition, dt: float) -> Dict[str, Any]:
        """Execute defensive evasion maneuver"""
        # Calculate evasion vector (away from target with lateral component)
        evade_angle = math.degrees(math.atan2(
            self.ship.y - target.y, 
            self.ship.x - target.x
        )) + random.uniform(-45, 45)  # Add randomness
        
        evade_distance = self.minimum_safe_distance * 1.5
        evade_x = self.ship.x + math.cos(math.radians(evade_angle)) * evade_distance
        evade_y = self.ship.y + math.sin(math.radians(evade_angle)) * evade_distance
        
        return {
            'maneuver': ManeuverType.DEFENSIVE_EVADE,
            'target_position': (evade_x, evade_y),
            'maneuver_description': ["Defensive evasion with random movement"]
        }
    
    def _execute_retreat_maneuver(self, target: SpaceShip, tactical_pos: TacticalPosition, dt: float) -> Dict[str, Any]:
        """Execute tactical retreat"""
        # Direct retreat away from target
        retreat_angle = math.degrees(math.atan2(
            self.ship.y - target.y, 
            self.ship.x - target.x
        ))
        
        retreat_distance = self.maximum_engagement_range
        retreat_x = self.ship.x + math.cos(math.radians(retreat_angle)) * retreat_distance
        retreat_y = self.ship.y + math.sin(math.radians(retreat_angle)) * retreat_distance
        
        return {
            'maneuver': ManeuverType.TACTICAL_RETREAT,
            'target_position': (retreat_x, retreat_y),
            'maneuver_description': ["Tactical retreat to safe distance"]
        }
    
    def _execute_locked_maneuver(self, target: SpaceShip, tactical_pos: TacticalPosition, dt: float) -> Dict[str, Any]:
        """Execute weapon-locked maneuver"""
        # Maintain current position while tracking target
        # Small adjustments to maintain optimal range
        if tactical_pos.distance_to_target < self.preferred_combat_range - 20:
            # Too close - back up slightly
            backup_angle = math.degrees(math.atan2(
                self.ship.y - target.y, 
                self.ship.x - target.x
            ))
            adjust_x = self.ship.x + math.cos(math.radians(backup_angle)) * 10
            adjust_y = self.ship.y + math.sin(math.radians(backup_angle)) * 10
        else:
            # Maintain position
            adjust_x, adjust_y = self.ship.x, self.ship.y
        
        return {
            'maneuver': ManeuverType.BROADSIDE_STRAFE,
            'target_position': (adjust_x, adjust_y),
            'maneuver_description': ["Weapon locked - maintaining position"]
        }
    
    def _should_fire_weapon(self, target: SpaceShip, tactical_pos: TacticalPosition, current_time: float) -> bool:
        """Determine if weapon should be fired"""
        # Check if weapon is ready
        if not self.ship.can_fire(current_time):
            return False
        
        # Check if target is in range
        if tactical_pos.distance_to_target > self.ship.weapon_range:
            return False
        
        # Check firing angle based on intent
        if self.current_intent == CombatIntent.STRAFE:
            # Strafing - wider firing angle
            max_fire_angle = 30.0
        elif self.current_intent == CombatIntent.LOCKED:
            # Locked - precise firing
            max_fire_angle = 10.0
        else:
            # Other intents - standard firing angle
            max_fire_angle = 20.0
        
        # Check if target is within firing cone
        if abs(tactical_pos.angle_to_target) <= max_fire_angle:
            return True
        
        return False
    
    def _update_target_tracking(self, target: SpaceShip, current_time: float):
        """Update target tracking data"""
        self.last_target_position = (target.x, target.y)
        
        # Update velocity history
        self.target_velocity_history.append((target.velocity_x, target.velocity_y))
        if len(self.target_velocity_history) > 10:  # Keep last 10 samples
            self.target_velocity_history.pop(0)
    
    def get_combat_stats(self) -> Dict[str, Any]:
        """Get combat navigation statistics"""
        return {
            'current_intent': self.current_intent.value,
            'aggression_level': self.aggression_level,
            'tactical_skill': self.tactical_skill,
            'risk_tolerance': self.risk_tolerance,
            'intent_switch_cooldown': self.intent_switch_cooldown,
            'combat_engagements': len(self.combat_history)
        }
