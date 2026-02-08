# DGT SDK (DuggerCore Game Tools)

**Version:** 2.0.0 (Kernel Bridge Edition)
**Target:** West Palm Beach Hub

## Overview
The DGT SDK is the modular "nervous system" of the RPG Core. It decouples the core simulation logic from the legacy rendering pipeline, enabling scalable fleet battles and genetic ship generation.

## 📦 Kernel (The Single Source of Truth)
Located in `src/dgt_core/kernel/`, this module holds the "Universal Truths" of the game world.

### Key Components
- **State (`state.py`)**: The immutable `GameState`, `ShipGenome`, and Entity dataclasses.
- **Constants (`constants.py`)**: Physics tuning, render layers, and system configuration.
- **Fleet Roles (`fleet_roles.py`)**: Definitions for `INTERCEPTOR`, `HEAVY`, and `SCOUT` roles.

```python
from src.dgt_core.kernel.state import GameState, ShipGenome
from src.dgt_core.kernel.fleet_roles import FleetRole

genome = ShipGenome(genome_id="alpha_01")
```

## 🏭 Generators ( The Ship-Wright)
Located in `src/dgt_core/generators/`, this module binds genetic traits to physical bodies.

### ShipWright usage
```python
from src.dgt_core.generators.ship_wright import ShipWright
from src.dgt_core.kernel.fleet_roles import FleetRole

# Convert genetics to physics
physics_specs = ShipWright.apply_genetics(genome, FleetRole.INTERCEPTOR)
print(physics_specs['max_thrust']) # Derived from aggression trait
```

## 🚀 Simulation (Physics Engine)
Located in `src/dgt_core/simulation/`, this module handles the Newtonian mechanics.
- **SpaceVoyagerEngine**: Real-time PID-controlled physics.
- **SpaceShip**: The physical entity in the simulation.

## 🌉 Legacy Bridge
To support older visual tools during migration:
- `src/dgt_core/engines/body/graphics_engine.py`: The adapter for legacy 160x144 rendering.
- Legacy files in `src/engines/body/` are now **shims** that redirect here.

## 🛠️ Testing
Run the 5v5 Stress Test to verify stability:
```bash
python demo_5v5_skirmish.py
```
**Success Metric:** Stable 60 FPS under 10-ship load.
