import pygame
from loguru import logger
from src.apps.slime_breeder.ui.scene_garden import GardenScene
from src.apps.slime_breeder.scenes.team_scene import TeamScene
from src.apps.slime_breeder.scenes.breeding_scene import BreedingScene
from src.apps.slime_breeder.scenes.race_scene import RaceScene
from src.apps.slime_breeder.scenes.scene_tower_defense import TowerDefenseScene
from src.apps.dungeon_crawler.ui.scene_the_room import TheRoomScene
from src.apps.dungeon_crawler.ui.scene_dungeon_room import DungeonRoomScene
from src.apps.slime_breeder.scenes.scene_dungeon_path import DungeonPathScene
from src.apps.dungeon_crawler.ui.scene_dungeon_combat import DungeonCombatScene
from src.apps.dungeon_crawler.ui.scene_inventory import InventoryOverlay
from src.shared.engine.scene_manager import SceneManager
from src.shared.ui.spec import SPEC_720
from src.shared.state.entity_registry import EntityRegistry
from src.shared.teams.roster_save import load_roster

def create_app() -> SceneManager:
    """Create and configure the Slime Breeder app."""
    # Initialize Manager with Standard Spec
    manager = SceneManager(
        width=SPEC_720.screen_width,
        height=SPEC_720.screen_height,
        title="Slime Breeder — Core Pass",
        fps=60,
        spec=SPEC_720
    )
    
    # Create shared entity registry from existing roster
    roster = load_roster()
    entity_registry = EntityRegistry.from_roster(roster)
    
    # Register scenes with shared registry
    manager.register("garden", GardenScene, entity_registry=entity_registry)
    manager.register("teams", TeamScene, entity_registry=entity_registry)
    manager.register("breeding", BreedingScene, entity_registry=entity_registry)
    manager.register("racing", RaceScene, entity_registry=entity_registry)
    manager.register("tower_defense", TowerDefenseScene, entity_registry=entity_registry)
    manager.register("dungeon", TheRoomScene, entity_registry=entity_registry)
    manager.register("dungeon_room", DungeonRoomScene, entity_registry=entity_registry)
    manager.register("dungeon_path", DungeonPathScene, entity_registry=entity_registry)
    manager.register("dungeon_combat", DungeonCombatScene, entity_registry=entity_registry)
    manager.register("inventory", InventoryOverlay, entity_registry=entity_registry)
    
    return manager

def main():
    logger.info("🚀 Launching Slime Breeder...")
    app = create_app()
    app.run("garden")

if __name__ == "__main__":
    main()
