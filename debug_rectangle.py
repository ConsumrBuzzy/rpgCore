import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.pixel_renderer import PixelRenderer, Pixel

# Debug rectangle drawing
renderer = PixelRenderer(20, 20)
pixel = Pixel(r=1, g=1, b=1, intensity=1.0)

# Draw outline
renderer.draw_rectangle(2, 2, 5, 3, pixel, fill=False)

# Check what was actually drawn
print("Rectangle from (2,2) with width=5, height=3:")
print("Expected corners: (2,2), (6,2), (2,4), (6,4)")

for y in range(1, 7):
    row = []
    for x in range(1, 8):
        if not renderer.pixels[y][x].is_empty():
            row.append('█')
        else:
            row.append('.')
    print(f"y={y}: {''.join(row)}")

# Check specific pixels
print(f"\nPixel (2,2): empty={renderer.pixels[2][2].is_empty()}")
print(f"Pixel (6,2): empty={renderer.pixels[6][2].is_empty()}")
print(f"Pixel (2,4): empty={renderer.pixels[2][4].is_empty()}")
print(f"Pixel (6,4): empty={renderer.pixels[6][4].is_empty()}")
