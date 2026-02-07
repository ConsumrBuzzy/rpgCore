"""
Voyager Logic: Deterministic Action Library (The Rails)

Pre-baked D&D archetypes to prevent "Decision Paralysis" in small LLMs.
"""

STANDARD_ACTIONS = {
    "aggressive": [
        {"id": "force", "label": "Intimidate the guard", "stat": "strength"},
        {"id": "combat", "label": "Start a brawl", "stat": "strength"},
        {"id": "investigate", "label": "Search for weapons", "stat": "intelligence"},
        {"id": "force", "label": "Kick down the door", "stat": "strength"}
    ],
    "curious": [
        {"id": "charm", "label": "Talk to the bartender", "stat": "charisma"},
        {"id": "investigate", "label": "Examine the rowdy crowd", "stat": "intelligence"},
        {"id": "finesse", "label": "Eavesdrop on conversations", "stat": "dexterity"},
        {"id": "investigate", "label": "Read the notices on the wall", "stat": "intelligence"}
    ],
    "tactical": [
        {"id": "finesse", "label": "Find the exit", "stat": "dexterity"},
        {"id": "investigate", "label": "Identify the strongest patron", "stat": "intelligence"},
        {"id": "distract", "label": "Cause a small commotion", "stat": "charisma"},
        {"id": "finesse", "label": "Hide in the shadows", "stat": "dexterity"}
    ],
    "chaotic": [
        {"id": "distract", "label": "Flip a table", "stat": "strength"},
        {"id": "charm", "label": "Buy everyone a round", "stat": "charisma"},
        {"id": "finesse", "label": "Pickpocket a patron", "stat": "dexterity"},
        {"id": "force", "label": "Scream at the ceiling", "stat": "strength"}
    ]
}
