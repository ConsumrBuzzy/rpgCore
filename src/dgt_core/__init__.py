"""
DGT Core SDK - ADR 139 Implementation
Unified Namespace for Cross-Project Reusability

This package provides the core "plumbing" for all DGT projects:
- Engines: Rendering, Physics, Input
- Simulation: Kinetics, Collisions, Pathfinding  
- Genetics: DNA, NEAT Bridge, Evolution
- Utils: Math, Logging, Configuration

Usage:
    from dgt_core.engines.ppu import PPUInputService
    from dgt_core.simulation.kinetics import KineticBody
    from dgt_core.genetics.neat_bridge import NeuroPilot
    from dgt_core.utils.math_v2 import Vector2D
"""

__version__ = "2.0.0"
__author__ = "DGT Development Team"

# Core imports for convenience
from .engines import *
from .simulation import *
from .genetics import *
from .utils import *

__all__ = [
    # Version info
    "__version__",
    "__author__",
    
    # Engine components (Legacy + New)
    "TriModalEngine", "BodyEngine", "EngineConfig",
    "DisplayDispatcher", "DisplayMode", "RenderPacket",
    "TerminalBody", "CockpitBody", "PPUBody",
    "create_tri_modal_engine", "create_legacy_engine",
    "GraphicsEngine", "RenderFrame", "TileBank", "Viewport", "RenderLayer",
    "TRI_MODAL_AVAILABLE",
    
    # Simulation components
    "SpaceShip", "SpaceVoyagerEngine", "NeuroPilot",
    "HeadlessSimulationServer", "PilotRegistry", "CommanderService",
    
    # Utility components
    "Vector2D", "ConfigManager", "Logger",
]

# Package initialization
import logging
from pathlib import Path

# Set up default logging for DGT Core
def setup_logging(level: str = "INFO", log_file: str = None):
    """Setup default logging for DGT Core SDK"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s'
        ))
        logging.getLogger().addHandler(file_handler)

# Auto-setup logging on import
setup_logging()

# Package metadata
PACKAGE_INFO = {
    "name": "dgt-core",
    "version": __version__,
    "description": "DGT Core SDK - Unified Game Development Framework",
    "author": __author__,
    "components": {
        "engines": ["Rendering", "Physics", "Input"],
        "simulation": ["Kinetics", "Collisions", "Pathfinding"],
        "genetics": ["DNA", "NEAT", "Evolution"],
        "utils": ["Math", "Logging", "Configuration"]
    }
}

def get_package_info():
    """Get package information"""
    return PACKAGE_INFO.copy()

def check_dependencies():
    """Check if all required dependencies are available"""
    required_packages = [
        "tkinter",
        "loguru", 
        "neat",
        "pathlib"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️  Missing dependencies: {missing}")
        return False
    
    return True

# Check dependencies on import
check_dependencies()
