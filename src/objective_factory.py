"""
Objective Factory: Procedural Narrative Goals

Generates specific goals for locations to drive the Voyager agent's
behavior and create a sense of purpose in the story.
"""

import random
from typing import List, Dict
from game_state import Goal
from world_map import Location

OBJECTIVE_TEMPLATES = {
    "tavern": [
        {
            "id": "steal_mug",
            "desc": "Steal the legendary Golden Mug from the bar.",
            "methods": ["stealth", "finesse", "combat"],
            "targets": ["Mug", "Bartender"]
        },
        {
            "id": "bribe_guard",
            "desc": "Bribe the guard to learn about the Obsidian Gate.",
            "methods": ["charm", "social", "gold"],
            "targets": ["Guard"]
        },
        {
            "id": "brawl",
            "desc": "Start a tavern brawl to cause a distraction.",
            "methods": ["combat", "force"],
            "targets": ["Patron", "Bartender"]
        }
    ],
    "plaza": [
        {
            "id": "infiltrate_noble",
            "desc": "Pickpocket the noble for a pass to the dungeon.",
            "methods": ["stealth", "finesse"],
            "targets": ["Noble"]
        },
        {
            "id": "preach",
            "desc": "Gather a crowd and preach to gain followers.",
            "methods": ["charm", "social"],
            "targets": ["Merchant", "Street Urchin"]
        },
        {
            "id": "investigate_fountain",
            "desc": "Find the secret lever hidden in the Great Fountain.",
            "methods": ["investigate", "search"],
            "targets": ["Fountain"]
        }
    ],
    "dungeon": [
        {
            "id": "defeat_sentinel",
            "desc": "Defeat the Void Sentinel guarding the gate.",
            "methods": ["combat", "force", "magic"],
            "targets": ["Sentinel"]
        },
        {
            "id": "unlock_gate",
            "desc": "Decode the runes on the Obsidian Gate.",
            "methods": ["investigate", "intelligence"],
            "targets": ["Gate"]
        }
    ]
}

def generate_goals_for_location(loc_id: str, template_id: str) -> List[Goal]:
    """Generates 1-2 goals for a specific location."""
    
    available = OBJECTIVE_TEMPLATES.get(template_id, OBJECTIVE_TEMPLATES["tavern"])
    num_goals = random.randint(1, 1) # Stick to 1 primary goal for now
    
    selected = random.sample(available, num_goals)
    goals = []
    
    for g_def in selected:
        goals.append(Goal(
            id=g_def["id"],
            description=g_def["desc"],
            method_tags=g_def["methods"],
            target_tags=g_def["targets"],
            type="short"
        ))
        
    return goals
