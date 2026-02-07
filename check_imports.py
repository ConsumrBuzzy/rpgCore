import sys
sys.path.append('src')
try:
    from deterministic_arbiter import DeterministicArbiter
    from game_loop import GameREPL
    print("Imports successful.")
except Exception as e:
    print(f"Import failed: {e}")
