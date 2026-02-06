"""
Main Game Loop: REPL for Semantic RPG

Orchestrates the Sense → Input → Resolve → Update cycle.
"""

from pathlib import Path

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from game_state import GameState, create_tavern_scenario
from narrative_engine import SyncNarrativeEngine
from semantic_engine import SemanticResolver, create_default_intent_library


class GameREPL:
    """
    Interactive game loop with Rich UI.
    
    Architecture:
    - SemanticResolver: Fast intent matching (~50ms)
    - NarrativeEngine: Rich outcome generation (~200-500ms)
    - GameState: Deterministic state updates
    """
    
    def __init__(
        self,
        state: GameState | None = None,
        save_path: Path | None = None
    ):
        """
        Initialize game with optional saved state.
        
        Args:
            state: Existing GameState (or None to create new)
            save_path: Path for auto-saving (default: ./savegame.json)
        """
        self.console = Console()
        self.save_path = save_path or Path("savegame.json")
        
        # Initialize game state
        if state:
            self.state = state
        elif self.save_path.exists():
            self.console.print(f"[green]Loading saved game from {self.save_path}[/green]")
            self.state = GameState.load_from_file(self.save_path)
        else:
            self.console.print("[yellow]Starting new game...[/yellow]")
            self.state = create_tavern_scenario()
        
        # Initialize semantic engine
        self.console.print("[cyan]Loading semantic engine...[/cyan]")
        intent_library = create_default_intent_library()
        self.resolver = SemanticResolver(intent_library, confidence_threshold=0.35)
        
        # Initialize narrative engine
        self.console.print("[cyan]Connecting to Ollama...[/cyan]")
        self.narrator = SyncNarrativeEngine(model_name='ollama:llama3.2', tone='humorous')
        
        logger.info("Game initialized successfully")
    
    def display_context(self) -> None:
        """Display current game context using Rich panels."""
        # Room description
        room_context = self.state.get_context_str()
        self.console.print(
            Panel(room_context, title="[bold blue]Current Scene[/bold blue]", border_style="blue")
        )
        
        # Player stats table
        stats_table = Table(show_header=False, box=None)
        stats_table.add_row("❤️  HP:", f"{self.state.player.hp}/{self.state.player.max_hp}")
        stats_table.add_row("💰 Gold:", str(self.state.player.gold))
        
        self.console.print(
            Panel(stats_table, title="[bold green]Player Stats[/bold green]", border_style="green")
        )
    
    def process_action(self, player_input: str) -> bool:
        """
        Process a player action through the semantic pipeline.
        
        Returns:
            True to continue game, False to quit
        """
        # Handle meta commands
        if player_input.lower() in ["quit", "exit", "q"]:
            return False
        
        if player_input.lower() in ["save"]:
            self.state.save_to_file(self.save_path)
            self.console.print("[green]Game saved![/green]")
            return True
        
        # Step 1: Resolve intent using semantic matching
        self.console.print("[dim]🔍 Resolving intent...[/dim]")
        
        intent_match = self.resolver.resolve_intent(player_input)
        
        if not intent_match:
            self.console.print(
                "[red]❌ I don't understand that action. Try rephrasing?[/red]"
            )
            return True
        
        self.console.print(
            f"[cyan]🎲 Intent: {intent_match.intent_id} "
            f"(confidence: {intent_match.confidence:.2f})[/cyan]"
        )
        
        # Step 2: Generate narrative outcome
        self.console.print("[dim]🧠 Generating outcome...[/dim]")
        
        context = self.state.get_context_str()
        
        outcome = self.narrator.generate_outcome_sync(
            intent_id=intent_match.intent_id,
            player_input=player_input,
            context=context,
            player_hp=self.state.player.hp,
            player_gold=self.state.player.gold
        )
        
        # Step 3: Display narrative
        success_icon = "✅" if outcome.success else "❌"
        narrative_color = "green" if outcome.success else "yellow"
        
        self.console.print(
            Panel(
                outcome.narrative,
                title=f"[bold {narrative_color}]{success_icon} Outcome[/bold {narrative_color}]",
                border_style=narrative_color
            )
        )
        
        # Step 4: Update game state
        # Try to infer target NPC from context
        target_npc = None
        room = self.state.rooms.get(self.state.current_room)
        if room and room.npcs:
            # Simple heuristic: pick first NPC mentioned in input
            for npc in room.npcs:
                if npc.name.lower() in player_input.lower():
                    target_npc = npc.name
                    break
            
            # Fallback: if only one NPC, assume they're the target
            if not target_npc and len(room.npcs) == 1:
                target_npc = room.npcs[0].name
        
        self.state.apply_outcome(outcome, target_npc)
        
        # Auto-save after each action
        self.state.save_to_file(self.save_path)
        
        # Check win/loss conditions
        if not self.state.player.is_alive():
            self.console.print(
                Panel(
                    "[bold red]You have died. Game Over.[/bold red]",
                    border_style="red"
                )
            )
            return False
        
        return True
    
    def run(self) -> None:
        """Start the game loop."""
        self.console.print(
            Panel(
                "[bold cyan]Welcome to the Semantic RPG![/bold cyan]\n\n"
                "Type natural language actions (e.g., 'I kick the table').\n"
                "Commands: [yellow]save[/yellow], [yellow]quit[/yellow]",
                border_style="cyan"
            )
        )
        
        while True:
            # Display current context
            self.console.print("\n" + "─" * 80 + "\n")
            self.display_context()
            
            # Get player input
            try:
                player_input = Prompt.ask("\n[bold]What do you do?[/bold]")
            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[yellow]Goodbye![/yellow]")
                break
            
            # Process action
            should_continue = self.process_action(player_input)
            
            if not should_continue:
                self.console.print("\n[yellow]Thanks for playing![/yellow]")
                break


def main():
    """Entry point for the game."""
    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        "game_debug.log",
        level="DEBUG",
        format="{time:HH:mm:ss} | {level} | {message}"
    )
    logger.add(
        lambda msg: None,  # Suppress console logs (Rich handles UI)
        level="INFO"
    )
    
    # Start game
    game = GameREPL()
    game.run()


if __name__ == "__main__":
    main()
