"""
Graphics Systems - Rendering and Visualization

Multi-modal rendering pipeline supporting various display modes and backends.

Provides:
- PixelRenderer: Low-resolution pixel art rendering with Unicode blocks
- TileBank: Game Boy-style 8x8 tile patterns and bank switching
- FXSystem: Particle emitter with pooling
- ParticleEffects: Explosion and effect templates
- ExhaustSystem: Engine trails and engine-type variations
- ColorPalette: Shared color utilities
"""

# Phase D Step 6 Graphics Systems
from .pixel_renderer import (
    PixelRenderer,
    Pixel,
    SpriteFrame,
    AnimatedSprite,
    BlockType,
    create_default_pixel_renderer,
    create_high_res_pixel_renderer,
    create_ultra_res_pixel_renderer,
)

from .tile_bank import (
    TileBank,
    TilePattern,
    TileType,
    create_default_tile_bank,
    create_large_tile_bank,
    create_minimal_tile_bank,
)

__all__ = [
    # PixelRenderer classes
    'PixelRenderer',
    'Pixel',
    'SpriteFrame',
    'AnimatedSprite',
    'BlockType',
    # PixelRenderer factories
    'create_default_pixel_renderer',
    'create_high_res_pixel_renderer',
    'create_ultra_res_pixel_renderer',
    # TileBank classes
    'TileBank',
    'TilePattern',
    'TileType',
    # TileBank factories
    'create_default_tile_bank',
    'create_large_tile_bank',
    'create_minimal_tile_bank',
]
