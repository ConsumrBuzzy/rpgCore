"""
Factories for Character Archetypes and Location Templates.
Enables rapid scenario prototyping and diverse Voyager behaviors.
"""

from typing import Dict, List
from game_state import PlayerStats, Room, NPC, Goal, Item
from objective_factory import generate_goals_for_location

class CharacterFactory:
    """Generates PlayerStats based on character archetypes."""
    
    ARCHETYPES = {
        "aggressive": {
            "name": "Warrior",
            "attributes": {"strength": 10, "dexterity": 2, "intelligence": -2, "charisma": -2},
            "gold": 20
        },
        "cunning": {
            "name": "Thief",
            "attributes": {"strength": -2, "dexterity": 10, "intelligence": 5, "charisma": 2},
            "gold": 100
        },
        "diplomatic": {
            "name": "Negotiator",
            "attributes": {"strength": -5, "dexterity": 0, "intelligence": 5, "charisma": 10},
            "gold": 200
        }
    }
    
    @classmethod
    def create(cls, archetype_name: str) -> PlayerStats:
        config = cls.ARCHETYPES.get(archetype_name.lower(), cls.ARCHETYPES["aggressive"])
        return PlayerStats(
            name=config["name"],
            attributes=config["attributes"],
            gold=config["gold"]
        )

class ScenarioFactory:
    """Generates a sequence of locations and goals (Story Frames)."""
    
    HEIST_FRAME = [
        {
            "id": "tavern",
            "name": "The Rusty Flagon",
            "description": "A dimly lit tavern where deals are made in shadows.",
            "npcs": ["Bartender", "Informant"],
            "tags": ["Low Light", "Noisy"],
            "goals_template": "tavern"
        },
        {
            "id": "market",
            "name": "Silver Market",
            "description": "A bustling plaza filled with merchants and guards.",
            "npcs": ["Merchant", "Guard"],
            "tags": ["Crowded", "High Alert"],
            "goals_template": "plaza"
        },
        {
            "id": "vault",
            "name": "The Obsidian Vault Entrance",
            "description": "A heavily guarded iron door leading deep underground.",
            "npcs": ["Sentinel", "Captain"],
            "tags": ["Anti-Magic", "Silent"],
            "goals_template": "dungeon"
        }
    ]
    
    @classmethod
    def get_heist_story(cls) -> List[Dict]:
        return cls.HEIST_FRAME
