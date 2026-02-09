"""
Mock RustSpriteScanner for runtime compatibility
"""

class RustSpriteScanner:
    def __init__(self, **kwargs):
        pass

    def analyze_sprite(self, pixels, width, height):
        return {
            'is_chest': False, 
            'is_character': False, 
            'is_decoration': False, 
            'is_material': True
        }

    def auto_clean_edges(self, pixels, width, height, threshold):
        return pixels
