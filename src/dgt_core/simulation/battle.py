"""
DGT Battle Service - ADR 129 Implementation
Active Time Battle (ATB) system for tactical space combat

Replaces racing mechanics with Final Fantasy-style turn-based combat
Supports genetic ship components and modular combat calculations
"""

import time
import random
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger
from .ship_genetics import ShipGenome, ship_genetic_registry


class BattleAction(str, Enum):
    """Battle action types"""
    ATTACK = "attack"
    DEFEND = "defend"
    REPAIR = "repair"
    SPECIAL = "special"
    ESCAPE = "escape"


class BattleStatus(str, Enum):
    """Battle participant status"""
    READY = "ready"
    ACTING = "acting"
    WAITING = "waiting"
    DEFEATED = "defeated"
    ESCAPED = "escaped"


@dataclass
class BattleParticipant:
    """Battle participant with ATB mechanics"""
    participant_id: str
    name: str
    genome: ShipGenome
    current_hp: float
    max_hp: float
    current_shields: float
    max_shields: float
    atb_progress: float = 0.0
    atb_speed: float = 1.0
    status: BattleStatus = BattleStatus.READY
    position: Tuple[float, float] = (0.0, 0.0)
    last_action_time: float = 0.0
    total_damage_dealt: float = 0.0
    total_damage_taken: float = 0.0
    
    def __post_init__(self):
        if self.atb_speed == 1.0:
            self.atb_speed = self.genome.calculate_atb_speed()
    
    def update_atb(self, dt: float):
        """Update Active Time Battle progress"""
        if self.status in [BattleStatus.READY, BattleStatus.WAITING]:
            self.atb_progress += self.atb_speed * dt
            if self.atb_progress >= 100.0:
                self.atb_progress = 100.0
                self.status = BattleStatus.READY
    
    def take_damage(self, damage: float, damage_type: str = "normal") -> float:
        """Apply damage with shields and armor"""
        if self.status == BattleStatus.DEFEATED:
            return 0.0
        
        # Shields absorb damage first
        shield_absorbed = min(self.current_shields, damage)
        remaining_damage = damage - shield_absorbed
        self.current_shields -= shield_absorbed
        
        # Armor reduces remaining damage
        stats = self.genome.calculate_combat_stats()
        armor_class = stats['armor_class']
        damage_reduction = max(0.1, 1.0 - (armor_class / 100.0))
        final_damage = remaining_damage * damage_reduction
        
        # Apply damage to HP
        hp_damage = min(self.current_hp, final_damage)
        self.current_hp -= hp_damage
        self.total_damage_taken += damage
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.status = BattleStatus.DEFEATED
        
        return damage
    
    def heal(self, amount: float):
        """Heal participant"""
        if self.status == BattleStatus.DEFEATED:
            return
        
        self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    def restore_shields(self, amount: float):
        """Restore shields"""
        if self.status == BattleStatus.DEFEATED:
            return
        
        self.current_shields = min(self.max_shields, self.current_shields + amount)
    
    def is_ready_for_action(self) -> bool:
        """Check if participant is ready for action"""
        return self.status == BattleStatus.READY and self.atb_progress >= 100.0
    
    def perform_action(self, action: BattleAction, target: Optional['BattleParticipant'] = None) -> Dict[str, Any]:
        """Perform battle action"""
        self.status = BattleStatus.ACTING
        self.last_action_time = time.time()
        self.atb_progress = 0.0
        
        result = {
            'action': action,
            'source': self.participant_id,
            'target': target.participant_id if target else None,
            'success': False,
            'damage': 0.0,
            'effects': []
        }
        
        if action == BattleAction.ATTACK and target:
            result = self._perform_attack(target, result)
        elif action == BattleAction.DEFEND:
            result = self._perform_defend(result)
        elif action == BattleAction.REPAIR:
            result = self._perform_repair(result)
        elif action == BattleAction.SPECIAL:
            result = self._perform_special(target, result)
        elif action == BattleAction.ESCAPE:
            result = self._perform_escape(result)
        
        # Reset to waiting after action
        self.status = BattleStatus.WAITING
        
        return result
    
    def _perform_attack(self, target: 'BattleParticipant', result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform attack action"""
        stats = self.genome.calculate_combat_stats()
        
        # Calculate hit chance
        base_hit_chance = stats['accuracy']
        evasion_penalty = target.genome.calculate_combat_stats()['evasion'] * 0.1
        hit_chance = max(0.1, base_hit_chance - evasion_penalty)
        
        # Roll to hit
        roll = random.random() * 100
        result['roll'] = roll
        
        if roll > hit_chance * 100:
            result['result'] = "MISS"
            return result
        
        # Calculate damage
        base_damage = stats['weapon_damage']
        fire_rate_bonus = stats['fire_rate'] * 0.1
        
        # Critical hit chance
        crit_chance = stats['critical_chance']
        is_critical = random.random() < crit_chance
        crit_multiplier = 2.0 if is_critical else 1.0
        
        # Final damage calculation
        damage = (base_damage + fire_rate_bonus) * crit_multiplier
        actual_damage = target.take_damage(damage, "energy")
        
        result['success'] = True
        result['damage'] = actual_damage
        result['result'] = "CRITICAL" if is_critical else "HIT"
        result['effects'].append(f"{'CRITICAL' if is_critical else 'HIT'} for {actual_damage:.1f} damage")
        
        self.total_damage_dealt += actual_damage
        
        return result
    
    def _perform_defend(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform defend action"""
        # Restore some shields
        shield_restore = 10.0 * self.genome.shield_frequency
        self.restore_shields(shield_restore)
        
        result['success'] = True
        result['effects'].append(f"Defensive stance - restored {shield_restore:.1f} shields")
        
        return result
    
    def _perform_repair(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform repair action"""
        # Repair some HP
        hp_restore = 15.0 * self.genome.structural_integrity
        self.heal(hp_restore)
        
        result['success'] = True
        result['effects'].append(f"Repairs - restored {hp_restore:.1f} HP")
        
        return result
    
    def _perform_special(self, target: Optional['BattleParticipant'], result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform special action"""
        # Special ability based on ship type
        if self.genome.hull_type.value == "stealth":
            # Stealth: Evasion boost
            result['effects'].append("Stealth mode activated - evasion increased")
        elif self.genome.engine_type.value == "warp":
            # Warp: Quick attack
            result['effects'].append("Warp strike - instant attack")
            if target:
                damage = self.genome.weapon_damage * 1.5
                actual_damage = target.take_damage(damage, "warp")
                result['damage'] = actual_damage
                result['success'] = True
        else:
            # Standard special: damage boost
            result['effects'].append("Overcharge - damage increased")
        
        return result
    
    def _perform_escape(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform escape action"""
        # Escape chance based on speed and evasion
        stats = self.genome.calculate_combat_stats()
        escape_chance = (stats['speed'] + stats['evasion']) / 200.0
        
        if random.random() < escape_chance:
            self.status = BattleStatus.ESCAPED
            result['success'] = True
            result['result'] = "ESCAPED"
            result['effects'].append("Successfully escaped from battle")
        else:
            result['success'] = False
            result['result'] = "FAILED_ESCAPE"
            result['effects'].append("Failed to escape")
        
        return result


@dataclass
class BattleArena:
    """Battle arena with tactical positioning"""
    width: float = 800.0
    height: float = 600.0
    obstacles: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate distance between two positions"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_optimal_range(self, attacker: BattleParticipant, target: BattleParticipant) -> str:
        """Get optimal combat range"""
        distance = self.get_distance(attacker.position, target.position)
        
        if distance < 150:
            return "close"
        elif distance < 400:
            return "medium"
        else:
            return "long"


class BattleService:
    """Active Time Battle service for tactical space combat"""
    
    def __init__(self):
        self.arena = BattleArena()
        self.participants: Dict[str, BattleParticipant] = {}
        self.battle_active = False
        self.battle_start_time: Optional[float] = None
        self.battle_log: List[Dict[str, Any]] = []
        self.current_turn: int = 0
        self.victory_conditions: Dict[str, Any] = {}
        
        logger.info("⚔️ Battle Service initialized")
    
    def setup_battle(self, participants: List[Dict[str, Any]]) -> bool:
        """Setup battle with participants"""
        if len(participants) < 2:
            logger.error("⚔️ Need at least 2 participants for battle")
            return False
        
        self.participants = {}
        
        for i, participant_data in enumerate(participants):
            participant_id = participant_data.get('id', f'participant_{i}')
            name = participant_data.get('name', f'Ship {i+1}')
            genome = participant_data.get('genome')
            
            if not genome:
                genome = ship_genetic_registry.generate_random_ship()
            
            # Calculate combat stats
            stats = genome.calculate_combat_stats()
            
            # Create participant
            battle_participant = BattleParticipant(
                participant_id=participant_id,
                name=name,
                genome=genome,
                current_hp=100.0,
                max_hp=100.0,
                current_shields=stats['shield_capacity'],
                max_shields=stats['shield_capacity'],
                position=self._get_start_position(i)
            )
            
            self.participants[participant_id] = battle_participant
        
        self.battle_active = True
        self.battle_start_time = time.time()
        self.current_turn = 0
        
        logger.info(f"⚔️ Battle setup complete: {len(self.participants)} participants")
        return True
    
    def _get_start_position(self, index: int) -> Tuple[float, float]:
        """Get starting position for participant"""
        # Arrange participants in a line
        spacing = self.arena.width / (len(self.participants) + 1)
        x = spacing * (index + 1)
        y = self.arena.height / 2
        return (x, y)
    
    def update_battle(self, dt: float) -> Dict[str, Any]:
        """Update battle state"""
        if not self.battle_active:
            return {}
        
        # Update ATB for all participants
        for participant in self.participants.values():
            if participant.status not in [BattleStatus.DEFEATED, BattleStatus.ESCAPED]:
                participant.update_atb(dt)
        
        # Check for battle end conditions
        if self._check_battle_end():
            self.battle_active = False
            return self._get_battle_result()
        
        # Process ready participants
        ready_participants = [p for p in self.participants.values() if p.is_ready_for_action()]
        
        if ready_participants:
            # Sort by ATB progress (fastest first)
            ready_participants.sort(key=lambda p: p.atb_progress, reverse=True)
            
            # Let fastest participant act
            actor = ready_participants[0]
            action_result = self._process_ai_action(actor)
            
            if action_result:
                self.battle_log.append(action_result)
                self.current_turn += 1
        
        return self._get_battle_state()
    
    def _process_ai_action(self, participant: BattleParticipant) -> Optional[Dict[str, Any]]:
        """Process AI action for participant"""
        # Simple AI logic
        alive_enemies = [p for p in self.participants.values() 
                        if p.participant_id != participant.participant_id 
                        and p.status not in [BattleStatus.DEFEATED, BattleStatus.ESCAPED]]
        
        if not alive_enemies:
            # No enemies, try to escape
            action = BattleAction.ESCAPE
            target = None
        else:
            # Choose target (weakest enemy)
            target = min(alive_enemies, key=lambda p: p.current_hp)
            
            # Choose action based on health
            if participant.current_hp < participant.max_hp * 0.3:
                # Low health - defend or escape
                if random.random() < 0.7:
                    action = BattleAction.DEFEND
                else:
                    action = BattleAction.ESCAPE
            elif participant.current_shields < participant.max_shields * 0.3:
                # Low shields - repair
                action = BattleAction.REPAIR
            else:
                # Normal - attack
                action = BattleAction.ATTACK
        
        return participant.perform_action(action, target)
    
    def _check_battle_end(self) -> bool:
        """Check if battle should end"""
        alive_participants = [p for p in self.participants.values() 
                            if p.status not in [BattleStatus.DEFEATED, BattleStatus.ESCAPED]]
        
        return len(alive_participants) <= 1
    
    def _get_battle_result(self) -> Dict[str, Any]:
        """Get battle results"""
        alive_participants = [p for p in self.participants.values() 
                            if p.status not in [BattleStatus.DEFEATED, BattleStatus.ESCAPED]]
        
        if alive_participants:
            winner = alive_participants[0]
            result_type = "VICTORY"
        else:
            winner = None
            result_type = "DRAW"
        
        return {
            'battle_ended': True,
            'result_type': result_type,
            'winner': winner.participant_id if winner else None,
            'duration': time.time() - self.battle_start_time if self.battle_start_time else 0,
            'total_turns': self.current_turn,
            'participants': {
                pid: {
                    'name': p.name,
                    'status': p.status.value,
                    'hp': p.current_hp,
                    'max_hp': p.max_hp,
                    'shields': p.current_shields,
                    'max_shields': p.max_shields,
                    'damage_dealt': p.total_damage_dealt,
                    'damage_taken': p.total_damage_taken
                }
                for pid, p in self.participants.items()
            }
        }
    
    def _get_battle_state(self) -> Dict[str, Any]:
        """Get current battle state"""
        return {
            'battle_active': self.battle_active,
            'battle_time': time.time() - self.battle_start_time if self.battle_start_time else 0,
            'current_turn': self.current_turn,
            'participants': {
                pid: {
                    'name': p.name,
                    'status': p.status.value,
                    'hp': p.current_hp,
                    'max_hp': p.max_hp,
                    'shields': p.current_shields,
                    'max_shields': p.max_shields,
                    'atb_progress': p.atb_progress,
                    'atb_speed': p.atb_speed,
                    'position': p.position,
                    'genome': p.genome.dict()
                }
                for pid, p in self.participants.items()
            },
            'arena': {
                'width': self.arena.width,
                'height': self.arena.height
            }
        }
    
    def get_battle_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get battle log entries"""
        return self.battle_log[-limit:]
    
    def cleanup_battle(self):
        """Clean up battle state"""
        self.participants = {}
        self.battle_active = False
        self.battle_start_time = None
        self.battle_log = []
        self.current_turn = 0
        
        logger.info("⚔️ Battle cleaned up")


# Global battle service instance
battle_service = BattleService()
