"""
Ship Genetics Proxy — Re-export from apps/rpg/logic/ship_genetics.py

Bypasses apps.rpg.__init__ (which eagerly loads world_engine)
by using importlib to load the module directly from disk.
"""

import importlib.util
import sys
from pathlib import Path

# Resolve the canonical source file
_genetics_path = Path(__file__).resolve().parent.parent / "rpg" / "logic" / "ship_genetics.py"
_spec = importlib.util.spec_from_file_location("apps.rpg.logic.ship_genetics", str(_genetics_path))
_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)

# Re-export public API
HullType = _module.HullType
WeaponType = _module.WeaponType
EngineType = _module.EngineType
ShipComponent = _module.ShipComponent
ShipGenome = _module.ShipGenome
ShipGeneticRegistry = _module.ShipGeneticRegistry
ship_genetic_registry = _module.ship_genetic_registry
