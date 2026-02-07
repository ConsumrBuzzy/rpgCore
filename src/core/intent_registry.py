"""
Hard-Coded Intent Registry - The Immutable Laws

These are the fundamental laws that the LLM must follow.
The Intent Registry is the constitutional document of the DGT system.
No modifications allowed without architectural review.
"""

from typing import Dict, List, Set, FrozenSet
from dataclasses import dataclass
from enum import Enum


class IntentCategory(Enum):
    """Categories of intents for organization and validation."""
    COMBAT = "combat"
    SOCIAL = "social"
    EXPLORATION = "exploration"
    UTILITY = "utility"
    MOVEMENT = "movement"


@dataclass(frozen=True)
class IntentLaw:
    """
    Immutable definition of an intent law.
    
    This represents a hard-coded rule that the LLM must follow.
    Once defined, these laws cannot be changed without architectural review.
    """
    intent_id: str
    description: str
    category: IntentCategory
    d20_attribute: str
    target_required: bool
    narrative_seeds: FrozenSet[str]
    validation_rules: FrozenSet[str]
    forbidden_modifiers: FrozenSet[str] = frozenset()


class IntentRegistry:
    """
    The Immutable Intent Registry - Constitutional Document of DGT
    
    This registry contains the hard-coded laws that govern all LLM interactions.
    The LLM is restricted to ONLY these intents - no exceptions, no extensions.
    """
    
    # CORE INTENTS - The Ten Commandments of DGT
    CORE_INTENTS: Dict[str, IntentLaw] = {
        "attack": IntentLaw(
            intent_id="attack",
            description="Engage in combat with target",
            category=IntentCategory.COMBAT,
            d20_attribute="strength",
            target_required=True,
            narrative_seeds=frozenset(["violence", "combat", "damage", "weapon", "armor"]),
            validation_rules=frozenset([
                "must_have_target",
                "target_must_be_alive", 
                "cannot_attack_self",
                "requires_weapon_or_unarmed"
            ]),
            forbidden_modifiers=frozenset(["peaceful", "friendly", "non_lethal"])
        ),
        
        "talk": IntentLaw(
            intent_id="talk",
            description="Communicate verbally with target",
            category=IntentCategory.SOCIAL,
            d20_attribute="charisma",
            target_required=True,
            narrative_seeds=frozenset(["dialogue", "conversation", "information", "social", "persuasion"]),
            validation_rules=frozenset([
                "must_have_target",
                "target_must_be_conscious",
                "requires_language_capability"
            ]),
            forbidden_modifiers=frozenset(["violent", "aggressive", "hostile"])
        ),
        
        "investigate": IntentLaw(
            intent_id="investigate",
            description="Examine environment or objects for information",
            category=IntentCategory.EXPLORATION,
            d20_attribute="intelligence",
            target_required=False,
            narrative_seeds=frozenset(["discovery", "clues", "details", "examination", "analysis"]),
            validation_rules=frozenset([
                "requires_perception",
                "cannot_investigate_empty_space"
            ]),
            forbidden_modifiers=frozenset(["combat", "social", "movement"])
        ),
        
        "use": IntentLaw(
            intent_id="use",
            description="Utilize an item or object",
            category=IntentCategory.UTILITY,
            d20_attribute="dexterity",
            target_required=False,
            narrative_seeds=frozenset(["tool", "item", "equipment", "mechanism", "function"]),
            validation_rules=frozenset([
                "requires_item_in_inventory",
                "item_must_be_usable",
                "cannot_use_broken_items"
            ]),
            forbidden_modifiers=frozenset(["create", "destroy", "transform"])
        ),
        
        "trade": IntentLaw(
            intent_id="trade",
            description="Exchange goods or services with target",
            category=IntentCategory.SOCIAL,
            d20_attribute="charisma",
            target_required=True,
            narrative_seeds=frozenset(["commerce", "bargaining", "wealth", "exchange", "value"]),
            validation_rules=frozenset([
                "must_have_target",
                "target_must_be_trader",
                "requires_tradeable_items"
            ]),
            forbidden_modifiers=frozenset(["steal", "force", "combat"])
        ),
        
        "steal": IntentLaw(
            intent_id="steal",
            description="Take items without permission (stealth)",
            category=IntentCategory.UTILITY,
            d20_attribute="dexterity",
            target_required=False,
            narrative_seeds=frozenset(["theft", "stealth", "crime", "covert", "illicit"]),
            validation_rules=frozenset([
                "requires_stealth_skill",
                "target_must_have_items",
                "cannot_steal_from_aware_targets"
            ]),
            forbidden_modifiers=frozenset(["honest", "legal", "peaceful"])
        ),
        
        "force": IntentLaw(
            intent_id="force",
            description="Apply physical strength to objects or barriers",
            category=IntentCategory.COMBAT,
            d20_attribute="strength",
            target_required=False,
            narrative_seeds=frozenset(["brute_force", "destruction", "breaking", "physical_power"]),
            validation_rules=frozenset([
                "requires_strength_check",
                "target_must_be_breakable",
                "cannot_force_living_beings"
            ]),
            forbidden_modifiers=frozenset(["gentle", "precise", "skillful"])
        ),
        
        "rest": IntentLaw(
            intent_id="rest",
            description="Recover health and fatigue",
            category=IntentCategory.UTILITY,
            d20_attribute="constitution",
            target_required=False,
            narrative_seeds=frozenset(["recovery", "healing", "rest", "fatigue", "endurance"]),
            validation_rules=frozenset([
                "requires_safe_location",
                "cannot_rest_in_combat",
                "limited_by_time"
            ]),
            forbidden_modifiers=frozenset(["combat", "movement", "exertion"])
        ),
        
        "help": IntentLaw(
            intent_id="help",
            description="Assist or aid target",
            category=IntentCategory.SOCIAL,
            d20_attribute="wisdom",
            target_required=True,
            narrative_seeds=frozenset(["assistance", "aid", "support", "cooperation", "healing"]),
            validation_rules=frozenset([
                "must_have_target",
                "target_must_need_help",
                "requires_helpful_intent"
            ]),
            forbidden_modifiers=frozenset(["harm", "hinder", "oppose"])
        ),
        
        "leave_area": IntentLaw(
            intent_id="leave_area",
            description="Exit current location to adjacent area",
            category=IntentCategory.MOVEMENT,
            d20_attribute="dexterity",
            target_required=False,
            narrative_seeds=frozenset(["transition", "travel", "movement", "exit", "journey"]),
            validation_rules=frozenset([
                "requires_exit_available",
                "cannot_leave_during_combat",
                "must_move_to_adjacent_area"
            ]),
            forbidden_modifiers=frozenset(["stay", "remain", "teleport"])
        )
    }
    
    # Immutable sets for fast validation
    VALID_INTENT_IDS: FrozenSet[str] = frozenset(CORE_INTENTS.keys())
    COMBAT_INTENTS: FrozenSet[str] = frozenset([
        intent for intent, law in CORE_INTENTS.items() 
        if law.category == IntentCategory.COMBAT
    ])
    SOCIAL_INTENTS: FrozenSet[str] = frozenset([
        intent for intent, law in CORE_INTENTS.items() 
        if law.category == IntentCategory.SOCIAL
    ])
    TARGET_REQUIRED_INTENTS: FrozenSet[str] = frozenset([
        intent for intent, law in CORE_INTENTS.items() 
        if law.target_required
    ])
    
    @classmethod
    def get_intent_law(cls, intent_id: str) -> IntentLaw:
        """
        Get the immutable law for an intent.
        
        Args:
            intent_id: The intent identifier
            
        Returns:
            IntentLaw object
            
        Raises:
            ValueError: If intent_id is not in registry
        """
        if intent_id not in cls.CORE_INTENTS:
            raise ValueError(f"Intent '{intent_id}' is not in the immutable registry")
        
        return cls.CORE_INTENTS[intent_id]
    
    @classmethod
    def validate_intent(cls, intent_id: str) -> bool:
        """
        Validate that an intent exists in the registry.
        
        Args:
            intent_id: The intent to validate
            
        Returns:
            True if valid, False otherwise
        """
        return intent_id in cls.VALID_INTENT_IDS
    
    @classmethod
    def get_intents_by_category(cls, category: IntentCategory) -> List[str]:
        """
        Get all intents in a specific category.
        
        Args:
            category: The intent category
            
        Returns:
            List of intent IDs in the category
        """
        return [
            intent_id for intent_id, law in cls.CORE_INTENTS.items()
            if law.category == category
        ]
    
    @classmethod
    def requires_target(cls, intent_id: str) -> bool:
        """
        Check if an intent requires a target.
        
        Args:
            intent_id: The intent to check
            
        Returns:
            True if target is required
        """
        if intent_id not in cls.CORE_INTENTS:
            return False
        
        return cls.CORE_INTENTS[intent_id].target_required
    
    @classmethod
    def get_d20_attribute(cls, intent_id: str) -> str:
        """
        Get the D20 attribute used for an intent.
        
        Args:
            intent_id: The intent to check
            
        Returns:
            D20 attribute name
        """
        if intent_id not in cls.CORE_INTENTS:
            return "strength"  # Default fallback
        
        return cls.CORE_INTENTS[intent_id].d20_attribute
    
    @classmethod
    def get_narrative_seeds(cls, intent_id: str) -> FrozenSet[str]:
        """
        Get narrative seeds for an intent.
        
        Args:
            intent_id: The intent to check
            
        Returns:
            Frozen set of narrative seed keywords
        """
        if intent_id not in cls.CORE_INTENTS:
            return frozenset(["action"])
        
        return cls.CORE_INTENTS[intent_id].narrative_seeds
    
    @classmethod
    def validate_intent_rules(cls, intent_id: str, context: Dict[str, Any]) -> List[str]:
        """
        Validate intent-specific rules against context.
        
        Args:
            intent_id: The intent to validate
            context: Game context for validation
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if intent_id not in cls.CORE_INTENTS:
            errors.append(f"Intent '{intent_id}' not in registry")
            return errors
        
        law = cls.CORE_INTENTS[intent_id]
        
        # Check target requirement
        if law.target_required and not context.get("target"):
            errors.append(f"Intent '{intent_id}' requires a target")
        
        # Check forbidden modifiers
        for modifier in law.forbidden_modifiers:
            if modifier in str(context.get("player_input", "")).lower():
                errors.append(f"Intent '{intent_id}' cannot use modifier '{modifier}'")
        
        return errors
    
    @classmethod
    def get_registry_summary(cls) -> Dict[str, Any]:
        """
        Get a summary of the intent registry.
        
        Returns:
            Dictionary with registry statistics
        """
        categories = {}
        for category in IntentCategory:
            categories[category.value] = len(cls.get_intents_by_category(category))
        
        return {
            "total_intents": len(cls.CORE_INTENTS),
            "categories": categories,
            "target_required_count": len(cls.TARGET_REQUIRED_INTENTS),
            "combat_intents": len(cls.COMBAT_INTENTS),
            "social_intents": len(cls.SOCIAL_INTENTS),
            "immutable": True,
            "last_modified": "2026-02-07",  # Golden Master date
            "version": "1.0.0"
        }


# Immutable validation functions - These cannot be changed
def validate_llm_output(llm_output: str) -> Dict[str, Any]:
    """
    Validate LLM output against immutable intent registry.
    
    Args:
        llm_output: Raw LLM output string
        
    Returns:
        Validation result with extracted intent
    """
    from core.simulator import IntentTaggingProtocol
    
    protocol = IntentTaggingProtocol()
    response = protocol.parse_player_input(llm_output)
    
    return {
        "valid": IntentRegistry.validate_intent(response.intent),
        "intent": response.intent,
        "confidence": response.confidence,
        "prose": response.prose,
        "errors": [] if IntentRegistry.validate_intent(response.intent) else ["Invalid intent"]
    }


def enforce_intent_laws(intent_id: str, game_context: Dict[str, Any]) -> bool:
    """
    Enforce the immutable intent laws.
    
    Args:
        intent_id: The intent to enforce
        game_context: Current game context
        
    Returns:
        True if intent complies with laws
    """
    # Validate intent exists
    if not IntentRegistry.validate_intent(intent_id):
        return False
    
    # Validate intent-specific rules
    errors = IntentRegistry.validate_intent_rules(intent_id, game_context)
    
    return len(errors) == 0


# Constitutional Preamble
CONSTITUTIONAL_PREAMBLE = """
DGT Intent Registry - Constitutional Document

These Ten Intents represent the fundamental laws governing all interactions
between probabilistic AI and deterministic game systems. No modification,
extension, or exception is permitted without unanimous architectural review.

The Intent Registry ensures:
1. LLM cannot corrupt deterministic game state
2. All actions follow predictable mathematical rules  
3. Narrative generation remains creative but bounded
4. System maintains single source of truth integrity

Ratified: February 7, 2026
Status: IMMUTABLE - GOLDEN MASTER
Version: 1.0.0
"""


# Export the immutable registry
__all__ = [
    'IntentRegistry',
    'IntentLaw', 
    'IntentCategory',
    'validate_llm_output',
    'enforce_intent_laws',
    'CONSTITUTIONAL_PREAMBLE'
]
