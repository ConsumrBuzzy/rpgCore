"""
Shell Engines Package - RPG Mechanics and Physics
"""

from .shell_engine import ShellEngine, create_shell_engine, ShellEntity, CombatAction
from .shell_wright import ShellWright, ShellAttributes, ShellRole, create_shell_wright
from .d20 import *

__all__ = [
    'ShellEngine', 'create_shell_engine', 'ShellEntity', 'CombatAction',
    'ShellWright', 'ShellAttributes', 'ShellRole', 'create_shell_wright',
    # D20 components
    'd20_core', 'd20_system'
]
