import pygame
import sys
from typing import Callable

class LegacySceneAdapter:
    """
    Wraps a standalone demo main() function as a Scene-compatible callable.
    Allows MainMenuScene to launch legacy apps without converting them
    to full Scene subclasses.
    
    Usage:
        adapter = LegacySceneAdapter(run_space_trader.main)
        adapter.launch()
    
    Contract:
        - Calls main() in the current process
        - On return, restores pygame display state for SceneManager
        - Does not crash if main() raises SystemExit (normal pygame quit)
    """
    
    def __init__(self, entry_func: Callable):
        self.entry_func = entry_func

    def launch(self) -> None:
        size = (1280, 720)
        caption = ("rpgCore", "")
        
        surface = pygame.display.get_surface()
        if surface:
            size = surface.get_size()
            caption = pygame.display.get_caption()
            
        try:
            self.entry_func()
        except SystemExit:
            pass
        except Exception as e:
            print(f"Legacy app crashed: {e}")
            
        # Most standalone apps call pygame.quit() on exit.
        if not pygame.get_init():
            pygame.init()
            
        pygame.display.set_mode(size)
        if caption[0]:
            pygame.display.set_caption(caption[0])
