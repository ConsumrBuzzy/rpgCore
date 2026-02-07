"""
DGT Runtime - The Minimal Game Engine
KISS Principle: Input -> Update -> Render -> Repeat
"""

import tkinter as tk
from tkinter import Canvas
import sys
import os
from typing import Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from dgt_state import DGTState, TileType
from dgt_physics import can_move_to
from graphics.ppu_tk_native_enhanced import EnhancedTkinterPPU, RenderEntity, DitherPresets
from utils.asset_loader import AssetLoader


class DGTRuntime:
    """The bicycle engine - simple 2D RPG runtime"""
    
    def __init__(self):
        # Initialize window
        self.root = tk.Tk()
        self.root.title("🎮 DGT Runtime - Playable Demo")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Game state
        self.state = DGTState()
        
        # Rendering
        self.canvas = Canvas(
            self.root,
            width=640,
            height=480,
            bg='#0a0a0a',
            highlightthickness=0
        )
        self.canvas.pack(pady=20)
        
        # Initialize PPU
        self.asset_loader = MockAssetLoader()
        self.ppu = EnhancedTkinterPPU(self.canvas, self.asset_loader)
        
        # UI elements
        self._setup_ui()
        
        # Input handling
        self._setup_input()
        
        # Game loop
        self.running = True
        self.update_counter = 0
        
        print("🎮 DGT Runtime Initialized")
        print("Controls: WASD to move, E to interact, ESC to quit")
    
    def _setup_ui(self) -> None:
        """Setup UI elements"""
        # Status bar
        self.status_frame = tk.Frame(self.root, bg='#2a2a2a')
        self.status_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.status_label = tk.Label(
            self.status_frame,
            text=self.state.message,
            font=("Courier", 10),
            fg='#00ff00',
            bg='#2a2a2a'
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Position label
        self.position_label = tk.Label(
            self.status_frame,
            text=f"Position: ({self.state.voyager.x}, {self.state.voyager.y})",
            font=("Courier", 10),
            fg='#ffffff',
            bg='#2a2a2a'
        )
        self.position_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def _setup_input(self) -> None:
        """Setup keyboard input"""
        self.root.bind('<Key>', self._on_key_press)
        self.root.bind('<KeyRelease>', self._on_key_release)
        
        # Track pressed keys
        self.pressed_keys = set()
    
    def _on_key_press(self, event) -> None:
        """Handle key press"""
        key = event.keysym.lower()
        self.pressed_keys.add(key)
        
        # Handle immediate actions
        if key == 'escape':
            self.running = False
            self.root.quit()
        elif key == 'e':
            self._handle_interaction()
    
    def _on_key_release(self, event) -> None:
        """Handle key release"""
        key = event.keysym.lower()
        self.pressed_keys.discard(key)
    
    def _handle_interaction(self) -> None:
        """Handle interaction key"""
        result = self.state.interact()
        print(f"🎯 {result}")
        self._update_status()
    
    def _process_input(self) -> None:
        """Process WASD input"""
        dx, dy = 0, 0
        
        if 'w' in self.pressed_keys:
            dy = -1
        elif 's' in self.pressed_keys:
            dy = 1
        
        if 'a' in self.pressed_keys:
            dx = -1
        elif 'd' in self.pressed_keys:
            dx = 1
        
        if dx != 0 or dy != 0:
            self._move_voyager(dx, dy)
    
    def _move_voyager(self, dx: int, dy: int) -> None:
        """Move voyager with physics check"""
        old_x, old_y = self.state.voyager.get_position()
        new_x, new_y = old_x + dx, old_y + dy
        
        if can_move_to(self.state, new_x, new_y):
            self.state.voyager.set_position(new_x, new_y)
            self.state.message = f"Moved to ({new_x}, {new_y})"
            print(f"🚶 Moved from ({old_x}, {old_y}) to ({new_x}, {new_y})")
        else:
            self.state.message = f"Blocked at ({new_x}, {new_y})!"
            print(f"🚫 Blocked at ({new_x}, {new_y})")
        
        self._update_status()
    
    def _update_status(self) -> None:
        """Update UI status"""
        self.status_label.config(text=self.state.message)
        x, y = self.state.voyager.get_position()
        self.position_label.config(text=f"Position: ({x}, {y})")
    
    def _render(self) -> None:
        """Render the game world"""
        # Clear previous frame
        self.ppu.clear_enhanced()
        
        # Create render entities from world state
        entities = []
        
        # Add world tiles
        for tile in self.state.tiles.values():
            layer = self._get_render_layer(tile.tile_type)
            
            entity = RenderEntity(
                world_pos=(tile.x, tile.y),
                sprite_id=tile.sprite_id,
                layer=layer,
                visible=True,
                material_id=self._get_material_id(tile.sprite_id),
                collision=tile.is_barrier,
                tags=["interactive"] if tile.tile_type == TileType.INTERACTIVE else [],
                metadata={"description": tile.description}
            )
            entities.append(entity)
        
        # Add voyager
        from graphics.ppu_tk_native_enhanced import RenderLayer
        voyager_entity = RenderEntity(
            world_pos=self.state.voyager.get_position(),
            sprite_id=self.state.voyager.sprite_id,
            layer=RenderLayer.ACTORS,
            visible=True,
            material_id="organic",
            collision=False,
            tags=["player", "animated"],
            metadata={"description": "The Voyager"}
        )
        entities.append(voyager_entity)
        
        # Render all entities
        self.ppu.render_enhanced_scene(entities)
        
        # Update animations
        self.ppu.update_frame()
    
    def _get_render_layer(self, tile_type):
        """Get render layer for tile type"""
        from graphics.ppu_tk_native_enhanced import RenderLayer
        if tile_type == TileType.BARRIER:
            return RenderLayer.FRINGE
        elif tile_type == TileType.INTERACTIVE:
            return RenderLayer.ACTORS
        else:
            return RenderLayer.SURFACES
    
    def _get_material_id(self, sprite_id: str) -> str:
        """Get material ID for sprite"""
        material_map = {
            "tree": "organic",
            "rock": "stone",
            "bush": "organic",
            "flower": "organic",
            "mushroom": "organic",
            "iron_lockbox": "metal",
            "voyager": "organic"
        }
        return material_map.get(sprite_id, "organic")
    
    def game_loop(self) -> None:
        """Main game loop - Input -> Update -> Render"""
        if not self.running:
            return
        
        # Input
        self._process_input()
        
        # Update (game logic would go here)
        self.update_counter += 1
        
        # Render
        self._render()
        
        # Schedule next frame (60 FPS = ~16ms)
        self.root.after(16, self.game_loop)
    
    def run(self) -> None:
        """Start the game"""
        print("🎮 Starting DGT Runtime...")
        print("🗺️ World Map:")
        self._print_world_map()
        
        # Start game loop
        self.game_loop()
        
        # Run tkinter main loop
        self.root.mainloop()
    
    def _print_world_map(self) -> None:
        """Print ASCII world map"""
        print("   " + "".join(str(i) for i in range(self.state.world_width)))
        print("  " + "─" * (self.state.world_width * 2 + 1))
        
        for y in range(self.state.world_height):
            row = f"{y:2d}│"
            for x in range(self.state.world_width):
                if (x, y) == self.state.voyager.get_position():
                    row += " @"
                else:
                    tile = self.state.get_tile(x, y)
                    if tile:
                        if tile.is_barrier:
                            row += " #"
                        elif tile.tile_type == TileType.INTERACTIVE:
                            row += " ?"
                        else:
                            row += " ◦"
                    else:
                        row += " ."
                row += " "
            print(row)
        
        print("  " + "─" * (self.state.world_width * 2 + 1))
        print("\nLegend: @=Voyager, #=Barrier, ?=Interactive, ◦=Object, .=Empty")


class MockAssetLoader:
    """Mock asset loader for demo"""
    
    def __init__(self):
        self.sprites = {}
        self._create_mock_sprites()
    
    def _create_mock_sprites(self) -> None:
        """Create mock sprites for demo"""
        # Create simple colored rectangles as sprites
        colors = {
            "voyager": "#00ff00",      # Green player
            "tree": "#2d5a27",        # Dark green tree
            "rock": "#757575",        # Gray rock
            "bush": "#4b7845",        # Light green bush
            "flower": "#ff69b4",      # Pink flower
            "mushroom": "#8b4513",    # Brown mushroom
            "iron_lockbox": "#9e9e9e" # Gray lockbox
        }
        
        for sprite_id, color in colors.items():
            # Create 16x16 sprite
            import tkinter as tk
            sprite = tk.PhotoImage(width=16, height=16)
            
            # Fill with color
            for y in range(16):
                for x in range(16):
                    sprite.put(color, (x, y))
            
            # Scale for display (4x)
            sprite = sprite.zoom(4, 4)
            self.sprites[sprite_id] = sprite
    
    def get_sprite(self, sprite_id: str):
        """Get sprite by ID"""
        return self.sprites.get(sprite_id)


def main():
    """Main entry point"""
    print("🎮 DGT Runtime - Minimal Game Engine")
    print("=" * 50)
    print("🚴 The Bicycle Engine - Simple, Functional, Fun")
    print("")
    print("Controls:")
    print("  WASD - Move the Voyager")
    print("  E    - Interact with objects")
    print("  ESC  - Quit game")
    print("")
    print("Objective:")
    print("  • Explore the world")
    print("  • Find the iron lockbox")
    print("  • Try to open it (need D20 >= 15)")
    print("")
    
    # Create and run runtime
    runtime = DGTRuntime()
    runtime.run()


if __name__ == "__main__":
    main()
