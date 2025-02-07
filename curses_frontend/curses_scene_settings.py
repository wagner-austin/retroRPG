# File: curses_scene_settings.py
# version: 2.3
#
# Summary:
#   Defines the SettingsScene using plugin layers.
#   The scene now uses layered drawing:
#       - Base background (lowest) for clearing/filling the screen.
#       - Background art (same art setup as LoadScene) above the base.
#       - Global rain effect (z_index=300 from global_effects_manager)
#       - Title and options menu (z_index=500) on top.
#
# Tags: scene, settings

import curses
import debug
from .scene_base import Scene
from .scene_layer_base import SceneLayer
from .curses_common import draw_screen_frame, draw_title, _draw_art, draw_instructions
from .where_curses_themes_lives import CURRENT_THEME

def _draw_settings_background_art(stdscr):
    stdscr.keypad(True)
    curses.curs_set(0)
    draw_screen_frame(stdscr)
    art_lines = CURRENT_THEME.get("crocodile_art", [])
    _draw_art(stdscr, art_lines, start_row=3, start_col=2)

class SettingsBaseLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="settings_base", z_index=0)
    
    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        # Clear the screen (base background)
        stdscr.erase()

class SettingsBackgroundLayer(SceneLayer):
    def __init__(self):
        # Background art layer above base.
        super().__init__(name="settings_background", z_index=100)

    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        _draw_settings_background_art(stdscr)
        # Legacy: Removed drawing title here.
        # draw_title(stdscr, "Settings (Placeholder)", row=1)

class SettingsMenuLayer(SceneLayer):
    def __init__(self):
        # Menu layer with title and options, on top.
        super().__init__(name="settings_menu", z_index=500)
        self.menu_lines = [
            "1) Toggle Debug",
            "q) Quit Settings"
        ]
        self.current_select_slot = 0

    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        # Draw header (title) at the top.
        draw_title(stdscr, "Settings (Placeholder)", row=1)
        max_h, max_w = stdscr.getmaxyx()
        start_row = 4
        row = start_row
        for i, line in enumerate(self.menu_lines):
            if i == self.current_select_slot:
                stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(row, 2, line)
            if i == self.current_select_slot:
                stdscr.attroff(curses.A_REVERSE)
            row += 1

    def handle_key(self, key):
        if key in (curses.KEY_UP, ord('w')):
            self.current_select_slot = max(0, self.current_select_slot - 1)
        elif key in (curses.KEY_DOWN, ord('s')):
            self.current_select_slot = min(len(self.menu_lines) - 1, self.current_select_slot + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            if self.current_select_slot == 0:
                debug.toggle_debug()
                return None
            elif self.current_select_slot == 1:
                return "QUIT"
        return None

class SettingsScene(Scene):
    def __init__(self):
        super().__init__()
        self.base_layer = SettingsBaseLayer()
        self.background_layer = SettingsBackgroundLayer()
        self.menu_layer = SettingsMenuLayer()
        # Layer order:
        # 1. Base background (z_index 0)
        # 2. Background art (z_index 100)
        # 3. Global rain effect (z_index 300, from global_effects_manager)
        # 4. Title and menu (z_index 500)
        self.layers = [self.base_layer, self.background_layer, self.menu_layer]

    def handle_input(self, key):
        result = self.menu_layer.handle_key(key)
        if result is not None:
            return result
        if key in (ord('q'), ord('Q'), 27):
            return "QUIT"
        return None