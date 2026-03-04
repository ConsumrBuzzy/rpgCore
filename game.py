# rpgCore — game launcher
# Usage:
#   python game.py              -> interactive menu
#   python game.py --list       -> list demos and exit
#   python game.py --run <id>   -> launch demo directly
#   python game.py --info <id>  -> show demo info and exit

import sys
from pathlib import Path

# Add src to the Python path if necessary for standalone runs
root_dir = Path(__file__).parent.absolute()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
    
from src.launcher.manifest import DemoManifest
from src.launcher.registry import DemoRegistry
from src.launcher.cli import CLILauncher

def main():
    manifest_path = root_dir / "demos.json"
    manifests = DemoManifest.load(manifest_path)
    registry = DemoRegistry(manifests)
    launcher = CLILauncher(registry)
    
    args = sys.argv[1:]
    
    if not args:
        # Launch Main Menu instead of directly booting garden
        from src.apps.slime_breeder.run_slime_breeder import create_app
        from src.shared.ui.scenes.scene_main_menu import MainMenuScene
        
        manager, entity_registry, game_session, dispatch_system, roster, roster_sync = create_app()
        manager.set_shared_state(
            entity_registry=entity_registry,
            game_session=game_session,
            dispatch_system=dispatch_system,
            roster=roster,
            roster_sync=roster_sync,
            registry=registry
        )
        
        manager.register("main_menu", MainMenuScene)
        manager.run("main_menu")
        return

    command = args[0]
    
    if command == "--list":
        launcher.print_list()
        
    elif command == "--run":
        if len(args) < 2:
            print("Error: --run requires a demo id")
            sys.exit(1)
        demo_id = args[1]
        demo = registry.get(demo_id)
        if not demo:
            print(f"Error: Unknown demo '{demo_id}'. Use --list to see available demos.")
            sys.exit(1)
        launcher.launch(demo)
        
    elif command == "--info":
        if len(args) < 2:
            print("Error: --info requires a demo id")
            sys.exit(1)
        demo_id = args[1]
        launcher.print_info(demo_id)
        
    else:
        print(f"Error: Unknown argument '{command}'")
        print("Usage:")
        print("  python game.py              -> interactive menu")
        print("  python game.py --list       -> list demos and exit")
        print("  python game.py --run <id>   -> launch demo directly")
        print("  python game.py --info <id>  -> show demo info and exit")
        sys.exit(1)

if __name__ == "__main__":
    main()
