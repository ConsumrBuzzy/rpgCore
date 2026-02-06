"""
Game State Machine

Deterministic state management for RPG world, player, and NPCs.
Uses Pydantic for validation and JSON serialization.
"""

from pathlib import Path
from typing import Dict, List, Literal

from loguru import logger
from pydantic import BaseModel, Field


class PlayerStats(BaseModel):
    """Player character statistics."""
    
    name: str = "Adventurer"
    hp: int = Field(default=100, ge=0, le=100)
    max_hp: int = 100
    gold: int = Field(default=50, ge=0)
    inventory: List[str] = Field(default_factory=list)
    
    def is_alive(self) -> bool:
        """Check if player is still alive."""
        return self.hp > 0
    
    def take_damage(self, amount: int) -> None:
        """Apply damage to player."""
        self.hp = max(0, self.hp - amount)
        logger.info(f"Player took {amount} damage. HP: {self.hp}/{self.max_hp}")
    
    def heal(self, amount: int) -> None:
        """Restore player HP."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        healed = self.hp - old_hp
        logger.info(f"Player healed for {healed}. HP: {self.hp}/{self.max_hp}")
    
    def modify_gold(self, amount: int) -> bool:
        """
        Add or remove gold.
        
        Returns:
            True if transaction succeeded, False if insufficient gold
        """
        if amount < 0 and self.gold < abs(amount):
            logger.warning(f"Insufficient gold: have {self.gold}, need {abs(amount)}")
            return False
        
        self.gold += amount
        logger.info(f"Gold {'gained' if amount > 0 else 'spent'}: {abs(amount)}. Total: {self.gold}")
        return True


class NPC(BaseModel):
    """Non-player character."""
    
    name: str
    state: Literal["neutral", "hostile", "distracted", "charmed", "dead"] = "neutral"
    hp: int = Field(default=50, ge=0)
    description: str = "An ordinary person"
    
    def is_alive(self) -> bool:
        """Check if NPC is still alive."""
        return self.state != "dead" and self.hp > 0
    
    def update_state(self, new_state: str) -> None:
        """Change NPC state (e.g., from neutral to hostile)."""
        old_state = self.state
        self.state = new_state  # type: ignore
        logger.info(f"{self.name}: {old_state} → {new_state}")


class Room(BaseModel):
    """A location in the game world."""
    
    name: str
    description: str
    npcs: List[NPC] = Field(default_factory=list)
    items: List[str] = Field(default_factory=list)
    exits: Dict[str, str] = Field(default_factory=dict)  # direction -> room_name


class GameState(BaseModel):
    """Complete state of the game world."""
    
    player: PlayerStats = Field(default_factory=PlayerStats)
    current_room: str = "tavern"
    rooms: Dict[str, Room] = Field(default_factory=dict)
    turn_count: int = 0
    
    def get_context_str(self) -> str:
        """
        Generate a text description of current context for LLM prompting.
        
        This is what the Narrative Engine sees when generating outcomes.
        """
        room = self.rooms.get(self.current_room)
        
        if not room:
            return "You are in an undefined location."
        
        context = f"Location: {room.name}\n{room.description}\n\n"
        
        if room.npcs:
            context += "NPCs present:\n"
            for npc in room.npcs:
                state_emoji = {
                    "neutral": "😐",
                    "hostile": "⚔️",
                    "distracted": "👀",
                    "charmed": "😍",
                    "dead": "💀"
                }
                emoji = state_emoji.get(npc.state, "")
                context += f"  - {npc.name} {emoji} ({npc.state}): {npc.description}\n"
        
        if room.items:
            context += f"\nItems: {', '.join(room.items)}\n"
        
        return context
    
    def apply_outcome(self, outcome: "ActionOutcome", target_npc: str | None = None) -> None:  # type: ignore
        """
        Update game state based on action outcome.
        
        Args:
            outcome: Result from NarrativeEngine
            target_npc: Name of NPC to update (if applicable)
        """
        # Update player HP
        if outcome.hp_change < 0:
            self.player.take_damage(abs(outcome.hp_change))
        elif outcome.hp_change > 0:
            self.player.heal(outcome.hp_change)
        
        # Update gold
        if outcome.gold_change != 0:
            self.player.modify_gold(outcome.gold_change)
        
        # Update NPC state
        if target_npc and self.current_room in self.rooms:
            room = self.rooms[self.current_room]
            for npc in room.npcs:
                if npc.name.lower() == target_npc.lower():
                    npc.update_state(outcome.npc_state)
                    break
        
        self.turn_count += 1
    
    def save_to_file(self, path: Path) -> None:
        """Persist game state to JSON."""
        path.write_text(self.model_dump_json(indent=2))
        logger.info(f"Game saved to {path}")
    
    @classmethod
    def load_from_file(cls, path: Path) -> "GameState":
        """Load game state from JSON."""
        data = path.read_text()
        logger.info(f"Game loaded from {path}")
        return cls.model_validate_json(data)


def create_tavern_scenario() -> GameState:
    """Create a pre-configured tavern scenario for testing."""
    state = GameState()
    
    # Build the tavern room
    tavern = Room(
        name="The Rusty Flagon",
        description=(
            "A dimly lit tavern filled with the smell of ale and roasted meat. "
            "Rowdy patrons fill the wooden tables."
        ),
        npcs=[
            NPC(
                name="Guard",
                state="neutral",
                hp=80,
                description="A stern-looking town guard watching the entrance"
            ),
            NPC(
                name="Bartender",
                state="neutral",
                hp=30,
                description="A burly man wiping mugs behind the bar"
            )
        ],
        items=["wooden table", "beer mug", "chair"],
        exits={"north": "town_square", "east": "alley"}
    )
    
    state.rooms["tavern"] = tavern
    state.current_room = "tavern"
    
    return state
