# File: pygame_layer_presets.py
# version: 1.1
#
# Summary:
#   Provides preset layers for pygame: a base erase layer that clears the screen
#   and a frame art layer that draws a decorative frame and art from the current theme.
#
# Tags: art, base, erase, pygame

from .pygame_scene_layer_base import SceneLayer
from .where_pygame_themes_lives import CURRENT_THEME
from .pygame_common import draw_screen_frame, _draw_art

class BaseEraseLayer(SceneLayer):
    def __init__(self, z_index=0):
        super().__init__(name="base_erase_layer", z_index=z_index)

    def draw(self, renderer, dt, context):
        # In pygame, clear the screen by filling it with a background color (e.g., black).
        screen = renderer.screen
        screen.fill((0, 0, 0))

class FrameArtLayer(SceneLayer):
    def __init__(self, art_key, z_index=100, start_row=3, start_col=2):
        super().__init__(name=f"frame_art_{art_key}", z_index=z_index)
        self.art_key = art_key
        self.start_row = start_row
        self.start_col = start_col

    def draw(self, renderer, dt, context):
        screen = renderer.screen
        draw_screen_frame(screen)
        lines = CURRENT_THEME.get(self.art_key, [])
        _draw_art(screen, lines, start_row=self.start_row, start_col=self.start_col)