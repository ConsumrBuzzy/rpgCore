"""
Death Arbiter - Final Judge Connecting D20 Mechanics to Graveyard
ADR 175: Death Arbitration Bridge for Permadeath System
"""

import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from loguru import logger

from ..engines.shells.d20.mechanics import D20Core, create_d20_core
from ..kernel.universal_registry import UniversalRegistry
from ..kernel.models import StoryFragment, asset_registry
from ..tactics.stakes_manager import DeathCause


@dataclass
class DeathResult:
    """Result of death arbitration"""
    ship_id: str
    survived: bool
    death_cause: Optional[DeathCause] = None
    roll_result: Optional[Dict[str, Any]] = None
    funeral_rite: Optional[StoryFragment] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class DeathArbiter:
    """The Final Judge. Connects the D20 roll to the Graveyard."""
    
    def __init__(self, registry: UniversalRegistry, d20_core: Optional[D20Core] = None):
        self.registry = registry
        self.d20_core = d20_core or create_d20_core()
        
        logger.debug("⚰️ DeathArbiter initialized - Final Judge active")
    
    def resolve_mortality(self, ship_id: str, death_cause: DeathCause = DeathCause.COMBAT_DESTRUCTION,
                        advantage: bool = False, disadvantage: bool = False) -> DeathResult:
        """
        Resolve mortality through D20 death save and graveyard arbitration
        
        Args:
            ship_id: ID of the ship to resolve
            death_cause: Cause of death situation
            advantage: Whether death save has advantage
            disadvantage: Whether death save has disadvantage
            
        Returns:
            DeathResult with outcome and details
        """
        logger.critical(f"⚰️ DEATH ARBITRATION: {ship_id} - {death_cause.value}")
        
        # Get ship data for context
        ship_data = self._get_ship_data(ship_id)
        if not ship_data:
            logger.error(f"⚰️ Ship {ship_id} not found for death arbitration")
            return DeathResult(ship_id=ship_id, survived=False, death_cause=death_cause)
        
        # Trigger the D20 Core death save
        roll, survived = self.d20_core.roll_death_save(
            modifier=self._calculate_death_save_modifier(ship_data),
            advantage=advantage,
            disadvantage=disadvantage
        )
        
        # Create roll result details
        roll_result = {
            "roll_total": roll.total,
            "natural_20": roll.natural_20,
            "natural_1": roll.natural_1,
            "modifier": self._calculate_death_save_modifier(ship_data),
            "advantage": advantage,
            "disadvantage": disadvantage
        }
        
        # Generate death result
        result = DeathResult(
            ship_id=ship_id,
            survived=survived,
            death_cause=death_cause if not survived else None,
            roll_result=roll_result
        )
        
        if not survived:
            # Systemic Permadeath
            self._execute_permadeath(result)
        else:
            # Stabilization
            self._execute_stabilization(result)
        
        return result
    
    def _get_ship_data(self, ship_id: str) -> Optional[Dict[str, Any]]:
        """Get ship data from registry"""
        try:
            return self.registry.get_ship_summary(ship_id)
        except Exception as e:
            logger.error(f"⚰️ Failed to get ship data for {ship_id}: {e}")
            return None
    
    def _calculate_death_save_modifier(self, ship_data: Dict[str, Any]) -> int:
        """Calculate death save modifier from ship data"""
        # Base modifier from Constitution (would be stored in ship data)
        # For now, use a simple calculation based on generation/victories
        base_modifier = 0
        
        # Bonus for high-generation ships (experience)
        generation = ship_data.get("generation", 1)
        if generation >= 10:
            base_modifier += 1
        if generation >= 25:
            base_modifier += 1
        if generation >= 50:
            base_modifier += 2  # Gen-50 veterans are tough
        
        # Penalty for recent deaths (curse)
        recent_deaths = self.registry.get_graveyard_summary().get("recent_deaths_24h", 0)
        if recent_deaths >= 3:
            base_modifier -= 1  # Bad luck curse
        
        return base_modifier
    
    def _execute_permadeath(self, result: DeathResult):
        """Execute permadeath sequence"""
        logger.critical(f"⚰️ EXECUTING PERMADEATH: {result.ship_id}")
        
        # Generate epitaph
        epitaph = self._generate_epitaph(result)
        
        # Move to graveyard
        success = self.registry.move_to_graveyard(
            ship_id=result.ship_id,
            death_cause=result.death_cause.value if result.death_cause else "unknown",
            epitaph=epitaph
        )
        
        if success:
            # Generate funeral rite
            funeral_rite = self._generate_funeral_rite(result)
            result.funeral_rite = funeral_rite
            
            logger.critical(f"⚰️ PERMADEATH COMPLETE: {result.ship_id} moved to graveyard")
        else:
            logger.error(f"⚰️ PERMADETH FAILED: Could not move {result.ship_id} to graveyard")
    
    def _execute_stabilization(self, result: DeathResult):
        """Execute stabilization sequence"""
        logger.info(f"⚰️ STABILIZATION: {result.ship_id} survived death save")
        
        # Would update ship state to stabilized
        # For now, just log the survival
        if result.roll_result and result.roll_result.get("natural_20"):
            logger.info(f"⚰️ MIRACLE: {result.ship_id} stabilized with Natural 20!")
        else:
            logger.info(f"⚰️ LUCKY: {result.ship_id} stabilized with roll {result.roll_result['roll_total']}")
    
    def _generate_epitaph(self, result: DeathResult) -> str:
        """Generate epitaph for fallen ship"""
        ship_data = self._get_ship_data(result.ship_id)
        if not ship_data:
            return f"{result.ship_id} - Lost to the void"
        
        generation = ship_data.get("generation", 1)
        victories = ship_data.get("total_victories", 0)
        engine_type = ship_data.get("last_engine_type", "unknown")
        
        # Death cause specific epitaphs
        if result.death_cause == DeathCause.COMBAT_DESTRUCTION:
            if result.roll_result and result.roll_result.get("natural_1"):
                return f"Gen-{generation} warrior, {victories} victories, claimed by a critical fumble"
            else:
                return f"Gen-{generation} champion, {victories} victories, fell in glorious combat"
        elif result.death_cause == DeathCause.RESOURCE_DEPLETION:
            return f"Gen-{generation} pioneer, {victories} victories, lost to the cold void"
        elif result.death_cause == DeathCause.ABANDONED:
            return f"Gen-{generation} explorer, {victories} victories, abandoned in the dark"
        else:
            return f"Gen-{generation} veteran, {victories} victories, systems failed"
    
    def _generate_funeral_rite(self, result: DeathResult) -> StoryFragment:
        """Generate funeral rite story fragment"""
        ship_data = self._get_ship_data(result.ship_id)
        
        # Create funeral story
        funeral_story = StoryFragment(
            fragment_id=f"funeral_{result.ship_id}_{int(result.timestamp)}",
            title=f"Funeral Rite: {result.ship_id}",
            content=self._create_funeral_content(result, ship_data),
            fragment_type="funeral_rite",
            mood="somber",
            setting="graveyard",
            tags=["perma", "death", "memorial", result.death_cause.value if result.death_cause else "unknown"],
            entity_references=[result.ship_id],
            prompt_template="The fleet mourns the loss of {ship_id}, a {generation}-generation warrior with {victories} victories. {epitaph}. Their legacy will be remembered in the halls of the Universal Registry.",
            context_data={
                "ship_id": result.ship_id,
                "generation": ship_data.get("generation", 1) if ship_data else 1,
                "victories": ship_data.get("total_victories", 0) if ship_data else 0,
                "epitaph": self._generate_epitaph(result),
                "death_cause": result.death_cause.value if result.death_cause else "unknown",
                "roll_result": result.roll_result
            }
        )
        
        # Store funeral story in asset registry
        # This would integrate with the story system
        logger.info(f"⚰️ Generated funeral rite for {result.ship_id}")
        
        return funeral_story
    
    def _create_funeral_content(self, result: DeathResult, ship_data: Optional[Dict[str, Any]]) -> str:
        """Create funeral rite content"""
        if not ship_data:
            return f"The ship {result.ship_id} has been lost to the void. Their sacrifice will be remembered."
        
        generation = ship_data.get("generation", 1)
        victories = ship_data.get("total_victories", 0)
        engine_type = ship_data.get("last_engine_type", "unknown")
        
        content = f"The ship {result.ship_id} has been lost to the void. "
        
        if result.death_cause == DeathCause.COMBAT_DESTRUCTION:
            if result.roll_result and result.roll_result.get("natural_1"):
                content += f"They fell to a critical fumble in the heat of battle. "
            else:
                content += f"They fought valiantly but were overwhelmed by enemy forces. "
        elif result.death_cause == DeathCause.RESOURCE_DEPLETION:
            content += f"Their systems failed, leaving them drifting in the endless dark. "
        elif result.death_cause == DeathCause.ABANDONED:
            content += f"They were abandoned when resources ran critically low. "
        else:
            content += f"Their systems failed catastrophically without warning. "
        
        content += f"As a Gen-{generation} warrior with {victories} victories, "
        content += f"they served with distinction in the {engine_type} engine. "
        
        if result.roll_result:
            roll = result.roll_result
            content += f"Their final death save was a {roll['roll_total']} "
            if roll.get("natural_20"):
                content += "(a miracle that was not enough). "
            elif roll.get("natural_1"):
                content += "(a critical fumble that sealed their fate). "
            else:
                content += f"against DC 10. "
        
        content += "The fleet mourns their loss, but their legacy will endure in the halls of the Universal Registry."
        
        return content
    
    def batch_resolve_deaths(self, death_events: list[Tuple[str, DeathCause]]) -> list[DeathResult]:
        """Resolve multiple death events efficiently"""
        results = []
        
        for ship_id, death_cause in death_events:
            result = self.resolve_mortality(ship_id, death_cause)
            results.append(result)
        
        logger.info(f"⚰️ Batch death resolution complete: {len(results)} events processed")
        return results
    
    def get_death_statistics(self) -> Dict[str, Any]:
        """Get death arbitration statistics"""
        graveyard_stats = self.registry.get_graveyard_summary()
        
        return {
            "total_deaths": graveyard_stats.get("total_deaths", 0),
            "deaths_by_cause": graveyard_stats.get("deaths_by_cause", {}),
            "average_generation": graveyard_stats.get("average_generation", 0),
            "total_victories_lost": graveyard_stats.get("total_victories_lost", 0),
            "recent_deaths": graveyard_stats.get("recent_deaths_24h", 0),
            "arbitration_active": True
        }
    
    def create_death_certificate(self, result: DeathResult) -> Dict[str, Any]:
        """Create official death certificate"""
        return {
            "certificate_id": f"death_cert_{result.ship_id}_{int(result.timestamp)}",
            "ship_id": result.ship_id,
            "death_timestamp": result.timestamp,
            "death_cause": result.death_cause.value if result.death_cause else "unknown",
            "survived": result.survived,
            "death_save": result.roll_result,
            "funeral_rite_id": result.funeral_rite.fragment_id if result.funeral_rite else None,
            "epitaph": self._generate_epitaph(result) if not result.survived else "Survived",
            "arbitrated_by": "DeathArbiter"
        }


# Factory function for easy initialization
def create_death_arbiter(registry: UniversalRegistry, d20_core: Optional[D20Core] = None) -> DeathArbiter:
    """Create a DeathArbiter instance"""
    return DeathArbiter(registry, d20_core)


# Global instance
death_arbiter = None  # Will be initialized with registry
