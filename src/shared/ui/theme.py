"""
UITheme - Design Token System

Canonical color and style definitions for all UI components.
This is the key piece that makes colors a single source of truth.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class UITheme:
    """Design token system with canonical colors and styling."""
    
    # Typography
    font_large: int = 18
    font_medium: int = 14
    font_small: int = 11
    font_tiny: int = 10
    
    # Base colors
    background: tuple = (20, 20, 30)
    surface: tuple = (30, 30, 45)
    surface_raised: tuple = (40, 40, 58)
    border: tuple = (60, 60, 80)
    border_active: tuple = (100, 100, 140)
    
    # Text colors  
    text_primary: tuple = (220, 220, 235)
    text_secondary: tuple = (160, 160, 180)
    text_dim: tuple = (100, 100, 120)
    text_accent: tuple = (255, 215, 0)
    
    # Status colors
    success: tuple = (80, 180, 80)
    warning: tuple = (220, 160, 40)
    danger: tuple = (200, 60, 60)
    info: tuple = (80, 140, 220)
    
    # Culture colors (canonical)
    culture_colors: Dict[str, tuple] = field(default_factory=lambda: {
        'ember':   (220, 80,  40),
        'gale':    (135, 206, 235),
        'marsh':   (60,  140, 60),
        'crystal': (220, 220, 240),
        'tundra':  (180, 200, 220),
        'tide':    (80,  80,  220),
        'void':    (180, 100, 220),
        'coastal': (80, 140, 180),
        'mixed':   (140, 140, 140),
    })
    
    # Stage colors (canonical)
    stage_colors: Dict[str, tuple] = field(default_factory=lambda: {
        'Hatchling': (255, 182, 193),
        'Juvenile':  (173, 216, 230),
        'Young':     (144, 238, 144),
        'Prime':     (255, 215, 0),
        'Veteran':   (100, 149, 237),
        'Elder':     (147, 112, 219),
    })
    
    # Tier colors (canonical)
    tier_colors: Dict[int, tuple] = field(default_factory=lambda: {
        1: (200, 200, 200),
        2: (200, 200, 200),
        3: (144, 238, 144),
        4: (144, 238, 144),
        5: (100, 149, 237),
        6: (100, 149, 237),
        7: (147, 112, 219),
        8: (255, 215, 0),
    })
    
    # Button colors
    button_colors: Dict[str, Dict[str, tuple]] = field(default_factory=lambda: {
        'primary':   {'bg': (80, 140, 220), 'text': (255, 255, 255), 'border': (100, 160, 240)},
        'secondary': {'bg': (60, 60, 80), 'text': (220, 220, 235), 'border': (80, 80, 100)},
        'danger':    {'bg': (200, 60, 60), 'text': (255, 255, 255), 'border': (220, 80, 80)},
        'ghost':     {'bg': (0, 0, 0, 0), 'text': (160, 160, 180), 'border': (100, 100, 120)},
        'warning':   {'bg': (220, 160, 40), 'text': (255, 255, 255), 'border': (240, 180, 60)},
    })
    
    # Panel colors
    panel_colors: Dict[str, Dict[str, tuple]] = field(default_factory=lambda: {
        'surface':  {'bg': (30, 30, 45), 'border': (60, 60, 80)},
        'card':     {'bg': (40, 40, 58), 'border': (80, 140, 220)},
        'overlay':  {'bg': (20, 20, 30, 230), 'border': (100, 100, 120)},
        'raised':   {'bg': (50, 50, 70), 'border': (80, 80, 100)},
    })


# Default theme instance
UITheme.DEFAULT = UITheme()
