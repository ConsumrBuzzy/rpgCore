"""
Asset Display Tool - WYSIWYG Sprite Gallery
ADR 085: The WYSIWYG Asset Bench

This tool treats the PPU as a Standalone Gallery for visual asset validation.
If a sprite is missing or the YAML is malformed, the tool provides immediate visual feedback.
"""

import os
import sys
import tkinter as tk
from typing import Dict, List, Tuple, Optional
from PIL import Image, ImageTk

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from graphics.ppu_tk_native import NativeTkinterPPU
from utils.asset_loader import AssetLoader
from core.system_config import create_default_config

class AssetDisplayTool:
    """WYSIWYG Asset Display Tool for visual asset validation"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🛠️ Asset Display Tool - WYSIWYG Sprite Gallery")
        self.root.geometry("800x600")
        
        # Asset systems
        self.config = create_default_config(seed="ASSET_DISPLAY")
        self.asset_loader = AssetLoader()
        self.ppu = None
        
        # UI Components
        self.canvas = None
        self.info_frame = None
        self.info_text = None
        self.hover_sprite_id = None
        
        # Initialize systems
        self._initialize_systems()
        self._build_ui()
        
        # Display assets
        self._display_all_assets()
        
        # Start the tool
        self.root.mainloop()
    
    def _initialize_systems(self) -> None:
        """Initialize asset systems"""
        try:
            # Initialize PPU
            self.ppu = NativeTkinterPPU(self.canvas, self.asset_loader)
            print("🎨 PPU initialized for asset display")
        except Exception as e:
            print(f"⚠️ PPU initialization failed: {e}")
    
    def _build_ui(self) -> None:
        """Build the UI components"""
        # Main frame
        main_frame = tk.Frame(self.root, bg="black")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🛠️ Asset Display Tool - WYSIWYG Sprite Gallery",
            bg="black",
            fg="cyan",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Canvas for sprite display
        canvas_frame = tk.Frame(main_frame, bg="black", relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=640,
            height=400,
            bg="#1a3a1a",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Info panel
        info_frame = tk.Frame(main_frame, bg="black", height=150)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.info_text = tk.Text(
            info_frame,
            height=8,
            bg="black",
            fg="green",
            font=("Courier", 9),
            wrap=tk.WORD
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="🛠️ Asset Display Tool Ready - Hover over sprites for details",
            bg="black",
            fg="yellow",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=(5, 0))
        
        # Bind hover events
        self.canvas.bind("<Motion>", self.on_hover)
        self.canvas.bind("<Leave>", self.on_leave)
    
    def _display_all_assets(self) -> None:
        """Display all registered assets in a grid"""
        if not self.asset_loader.registry:
            self.info_text.insert(tk.END, "❌ No assets loaded - check YAML syntax\n")
            return
        
        # Get all sprite IDs
        sprite_ids = list(self.asset_loader.registry.keys())
        
        if not sprite_ids:
            self.info_text.insert(tk.END, "❌ No sprites found in registry\n")
            return
        
        # Calculate grid dimensions
        grid_size = 8  # 8x8 grid
        cell_size = 80  # 80x80 pixels per cell
        padding = 10
        
        # Display sprites in grid
        row, col = 0, 0
        for sprite_id in sprite_ids:
            if row >= grid_size:
                break
                
            x = padding + col * (cell_size + padding)
            y = padding + row * (cell_size + padding)
            
            try:
                sprite = self.asset_loader.registry[sprite_id]
                if sprite:
                    self.canvas.create_image(
                        x + cell_size // 2,
                        y + cell_size // 2,
                        image=sprite,
                        anchor="center",
                        tags=(sprite_id, "asset")
                    )
                    
                    # Add label
                    self.canvas.create_text(
                        x + cell_size // 2,
                        y + cell_size + 20,
                        text=sprite_id[:10],  # Truncate long names
                        fill="white",
                        font=("Arial", 8),
                        tags=(sprite_id, "label")
                    )
                    
                    # Next position
                    col += 1
                    if col >= grid_size:
                        col = 0
                        row += 1
                
            except Exception as e:
                # Show pink X for missing sprite
                self.canvas.create_rectangle(
                    x, y,
                    x + cell_size, y + cell_size,
                    fill="pink",
                    outline="red",
                    width=2
                )
                self.canvas.create_text(
                    x + cell_size // 2,
                    y + cell_size // 2,
                    text="X",
                    fill="red",
                    font=("Arial", 20, "bold"),
                    tags=(sprite_id, "error")
                )
                self.canvas.create_text(
                    x + cell_size // 2,
                    y + cell_size + 20,
                    text=f"❌ {sprite_id}",
                    fill="red",
                    font=("Arial", 8),
                    tags=(sprite_id, "error")
                )
        
        self.status_label.config(text=f"🛠️ Displayed {len(sprite_ids)} assets in {grid_size}x{grid_size} grid")
        self.info_text.insert(tk.END, f"✅ Successfully displayed {len(sprite_ids)} assets\n")
    
    def on_hover(self, event) -> None:
        """Handle mouse hover over sprites"""
        # Find what's under the cursor
        x, y = event.x, event.y
        
        # Find closest sprite
        closest_item = self.canvas.find_closest(x, y)
        if closest_item:
            tags = self.canvas.gettags(closest_item)
            if tags:
                sprite_id = tags[0]
                if sprite_id != self.hover_sprite_id:
                    # Clear previous hover
                    if self.hover_sprite_id:
                        self.canvas.itemconfig(self.hover_sprite_id, outline="")
                    
                    # Set new hover
                    self.hover_sprite_id = sprite_id
                    self.canvas.itemconfig(closest_item, outline="yellow", width=3)
                    
                    # Display sprite info
                    self.display_sprite_info(sprite_id)
    
    def on_leave(self, event) -> None:
        """Handle mouse leave"""
        if self.hover_sprite_id:
            self.canvas.itemconfig(self.hover_sprite_id, outline="")
            self.hover_sprite_id = None
            self.info_text.delete(1.0, tk.END)
            self.status_label.config(text="🛠️ Asset Display Tool Ready - Hover over sprites for details")
    
    def display_sprite_info(self, sprite_id: str) -> None:
        """Display detailed information about a sprite"""
        try:
            # Clear previous info
            self.info_text.delete(1.0, tk.END)
            
            # Get sprite
            sprite = self.asset_loader.registry.get(sprite_id)
            if not sprite:
                self.info_text.insert(tk.END, f"❌ Sprite '{sprite_id}' not found in registry\n")
                return
            
            # Get asset definition if available
            asset_def = self.asset_loader.get_asset_definition(sprite_id)
            
            # Display information
            info = f"🎨 Sprite: {sprite_id}\n"
            
            if asset_def:
                info += f"📋 Material: {getattr(asset_def, 'material', 'unknown')}\n"
                info += f"🏷️ Integrity: {getattr(asset_def, 'integrity', 'unknown')}\n"
                info += f"🏷️ Collision: {getattr(asset_def, 'collision', 'unknown')}\n"
                
                tags = getattr(asset_def, 'tags', [])
                if tags:
                    info += f"🏷️ Tags: {', '.join(tags)}\n"
                
                d20_checks = getattr(asset_def, 'd20_checks', {})
                if d20_checks:
                    info += f"🎲 D20 Checks:\n"
                    for check_name, check_data in d20_checks.items():
                        info += f"  • {check_name}: DC {check_data.get('difficulty', 'N/A')}\n"
                
                triggers = getattr(asset_def, 'triggers', {})
                if triggers:
                    info += f"⚡ Triggers:\n"
                    for trigger_name, trigger_data in triggers.items():
                        info += f"  • {trigger_name}: {trigger_data}\n"
            
            info += f"🖼️ Size: {sprite.width}x{sprite.height} pixels\n"
            info += f"🎨 Type: {type(sprite).__name__}\n"
            info += "-" * 40 + "\n"
            
            self.info_text.insert(tk.END, info)
            
        except Exception as e:
            self.info_text.insert(tk.END, f"❌ Error displaying info for '{sprite_id}': {e}\n")

if __name__ == "__main__":
    tool = AssetDisplayTool()
