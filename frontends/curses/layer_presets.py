# FileName: layer_presets.py

# version 1.1

# Summary: Draws base erase layer and frame art layer

# Tags: art, base, erase

from .scene_layer_base import SceneLayer
from .where_curses_themes_lives import CURRENT_THEME
from .curses_common import draw_screen_frame, _draw_art

class BaseEraseLayer(SceneLayer):
    def __init__(self, z_index=0):
        super().__init__(name="base_erase_layer", z_index=z_index)

    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        stdscr.erase()

class FrameArtLayer(SceneLayer):
    def __init__(self, art_key, z_index=100, start_row=3, start_col=2):
        super().__init__(name=f"frame_art_{art_key}", z_index=z_index)
        self.art_key = art_key
        self.start_row = start_row
        self.start_col = start_col

    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        draw_screen_frame(stdscr)
        lines = CURRENT_THEME.get(self.art_key, [])
        _draw_art(stdscr, lines, start_row=self.start_row, start_col=self.start_col)
