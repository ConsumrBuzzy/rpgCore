
import sys
import os
sys.path.insert(0, os.path.abspath("src"))

print("DEBUG: Importing rpg_core.foundation.vector")
from rpg_core.foundation.vector import Vector2
print("DEBUG: Success importing vector")

print("DEBUG: Importing rpg_core.systems.body.kinetics")
from rpg_core.systems.body.kinetics import KineticEntity
print("DEBUG: Success importing kinetics")

print("DEBUG: Importing rpg_core.foundation.utils.performance_monitor")
from rpg_core.foundation.utils.performance_monitor import PerformanceMonitor
print("DEBUG: Success importing performance_monitor")

print("DEBUG: Importing rpg_core.systems.graphics.fx.exhaust_system")
from rpg_core.systems.graphics.fx.exhaust_system import ExhaustSystem
print("DEBUG: Success importing exhaust_system")

print("DEBUG: All imports successful")
