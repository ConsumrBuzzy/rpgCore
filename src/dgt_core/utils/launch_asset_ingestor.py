#!/usr/bin/env python3
"""
Launch Asset Ingestor - ADR 094: The Automated Harvesting Protocol
Test the DGT Asset Ingestor with sample spritesheet
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.asset_ingestor import create_asset_ingestor

def create_sample_spritesheet():
    """Create a sample spritesheet for testing"""
    from PIL import Image, ImageDraw
    
    # Create a sample spritesheet (4x4 grid of 16x16 sprites)
    spritesheet = Image.new('RGB', (64, 64), '#ffffff')
    draw = ImageDraw.Draw(spritesheet)
    
    # Draw different sprite types
    sprites = [
        # Row 0: Organic materials
        {'pos': (0, 0), 'color': '#2d5a27', 'type': 'grass'},
        {'pos': (16, 0), 'color': '#3a6b35', 'type': 'leaves'},
        {'pos': (32, 0), 'color': '#4b7845', 'type': 'flowers'},
        {'pos': (48, 0), 'color': '#5c8745', 'type': 'vines'},
        
        # Row 1: Wood materials
        {'pos': (0, 16), 'color': '#5d4037', 'type': 'wood'},
        {'pos': (16, 16), 'color': '#6b5447', 'type': 'bark'},
        {'pos': (32, 16), 'color': '#7b6557', 'type': 'plank'},
        {'pos': (48, 16), 'color': '#8b7667', 'type': 'stump'},
        
        # Row 2: Stone materials
        {'pos': (0, 32), 'color': '#757575', 'type': 'stone'},
        {'pos': (16, 32), 'color': '#858585', 'type': 'granite'},
        {'pos': (32, 32), 'color': '#959595', 'type': 'marble'},
        {'pos': (48, 32), 'color': '#a5a5a5', 'type': 'slate'},
        
        # Row 3: Metal materials
        {'pos': (0, 48), 'color': '#9e9e9e', 'type': 'metal'},
        {'pos': (16, 48), 'color': '#aeaeae', 'type': 'steel'},
        {'pos': (32, 48), 'color': '#bebebe', 'type': 'silver'},
        {'pos': (48, 48), 'color': '#cecece', 'type': 'gold'},
    ]
    
    for sprite in sprites:
        x, y = sprite['pos']
        color = sprite['color']
        sprite_type = sprite['type']
        
        # Draw sprite with some variation
        if sprite_type in ['grass', 'leaves', 'flowers', 'vines']:
            # Organic - add some texture
            for dy in range(16):
                for dx in range(16):
                    if (dx + dy) % 3 == 0:
                        # Lighter variant
                        r = int(color[1:3], 16)
                        g = int(color[3:5], 16)
                        b = int(color[5:7], 16)
                        lighter = f"#{min(255, r + 20):02x}{min(255, g + 20):02x}{min(255, b + 20):02x}"
                        draw.point((x + dx, y + dy), fill=lighter)
                    elif (dx + dy) % 5 == 0:
                        # Darker variant
                        r = int(color[1:3], 16)
                        g = int(color[3:5], 16)
                        b = int(color[5:7], 16)
                        darker = f"#{max(0, r - 20):02x}{max(0, g - 20):02x}{max(0, b - 20):02x}"
                        draw.point((x + dx, y + dy), fill=darker)
                    else:
                        draw.point((x + dx, y + dy), fill=color)
        elif sprite_type in ['wood', 'bark']:
            # Wood - add grain lines
            for dy in range(0, 16, 4):
                draw.line([(x, y + dy), (x + 15, y + dy)], fill=color)
        elif sprite_type in ['stone', 'granite', 'marble', 'slate']:
            # Stone - add texture
            for dy in range(16):
                for dx in range(16):
                    if (dx + dy) % 2 == 0:
                        draw.point((x + dx, y + dy), fill=color)
        elif sprite_type in ['metal', 'steel', 'silver', 'gold']:
            # Metal - add sheen
            for dy in range(0, 16, 2):
                for dx in range(0, 16, 2):
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    sheen = f"#{min(255, r + 40):02x}{min(255, g + 40):02x}{min(255, b + 40):02x}"
                    draw.point((x + dx, y + dy), fill=sheen)
        else:
            # Default fill
            draw.rectangle([x, y, x + 15, y + 15], fill=color)
    
    return spritesheet

def main():
    """Main entry point"""
    print("=== DGT Asset Ingestor Test ===")
    print("Creating sample spritesheet...")
    
    # Create sample spritesheet
    sample_path = Path("sample_spritesheet.png")
    spritesheet = create_sample_spritesheet()
    spritesheet.save(sample_path)
    
    print(f"✅ Created sample spritesheet: {sample_path}")
    print("🎨 Starting Asset Ingestor...")
    
    # Launch ingestor
    ingestor = create_asset_ingestor()
    
    # Auto-load the sample spritesheet
    ingestor.spritesheet_path = sample_path
    ingestor.spritesheet_image = spritesheet
    ingestor.grid_cols = 4
    ingestor.grid_rows = 4
    
    # Update UI
    ingestor.file_label.config(text=f"Loaded: {sample_path.name}")
    ingestor.status_label.config(text="Sample spritesheet loaded successfully", foreground="green")
    
    # Display spritesheet
    ingestor._display_spritesheet()
    
    print("🎨 Asset Ingestor ready!")
    print("📋 Instructions:")
    print("  1. Click 'Slice Grid' to harvest all sprites")
    print("  2. Select individual sprites with mouse drag")
    print("  3. Click 'Bake Selection' to process selected sprite")
    print("  4. Click 'Generate Meta' to see YAML structure")
    print("  5. Click 'Export All' to save all assets")
    print("  6. Toggle 'Grayscale Mode' for DGT compatibility")
    print("  7. Use 'Zoom In/Out' to inspect details")
    
    # Run the ingestor
    ingestor.run()

if __name__ == "__main__":
    main()
