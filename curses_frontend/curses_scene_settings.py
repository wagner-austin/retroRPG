# File: curses_scene_settings.py
# version: 2.4 (updated to use shared layers and standardized text colors similar to the home Scene)
# Summary:
#   Defines the SettingsScene using plugin layers.
#   The scene now uses layered drawing:
#       - Base background (lowest) for clearing/filling the screen.
#       - Background art (using shared art drawing) above the base.
#       - Global effects (z_index=300, if any)
#       - Menu (z_index=400) and Title (z_index=500) on top.
# Tags: scene, settings

import curses
import tools.debug as debug
from .scene_base import Scene
from .scene_layer_base import SceneLayer
from .curses_common import draw_title
from .curses_selector_highlight import draw_global_selector_line


class SettingsTitleLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="settings_title", z_index=500)

    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        draw_title(stdscr, "Settings (Placeholder)", row=1)


class SettingsMenuLayer(SceneLayer):
    def __init__(self):
        # Set z_index to 400 so that it is drawn below the title layer.
        super().__init__(name="settings_menu", z_index=400)
        self.menu_lines = [
            "1) Toggle Debug",
            "2) Return"
        ]
        self.current_select_slot = 0

    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        max_h, max_w = stdscr.getmaxyx()
        start_row = 4
        row = start_row
        for i, line in enumerate(self.menu_lines):
            is_selected = (i == self.current_select_slot)
            draw_global_selector_line(
                stdscr, row, line,
                is_selected=is_selected,
                frame=dt  # use dt as frame count for any animation effects
            )
            row += 1

        # Deprecated manual drawing (no longer used):
        # row = start_row
        # for i, line in enumerate(self.menu_lines):
        #     if i == self.current_select_slot:
        #         stdscr.attron(curses.A_REVERSE)
        #     stdscr.addstr(row, 2, line)
        #     if i == self.current_select_slot:
        #         stdscr.attroff(curses.A_REVERSE)
        #     row += 1

    def handle_key(self, key):
        if key in (ord('v'), ord('V')):
            debug.toggle_debug()
        if key in (curses.KEY_UP, ord('w'), ord('W')):
            self.current_select_slot = max(0, self.current_select_slot - 1)
        elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
            self.current_select_slot = min(len(self.menu_lines) - 1, self.current_select_slot + 1)
        elif key in (curses.KEY_ENTER, 10, 13, 32):
            if self.current_select_slot == 0:
                debug.toggle_debug()
                return None
            elif self.current_select_slot == 1:
                return "QUIT"
        return None


class SettingsScene(Scene):
    def __init__(self):
        super().__init__()
        # Use the shared layers from layer_presets.
        from .layer_presets import BaseEraseLayer, FrameArtLayer
        self.base_layer = BaseEraseLayer()
        self.background_layer = FrameArtLayer("crocodile_art", z_index=100)
        self.menu_layer = SettingsMenuLayer()
        self.title_layer = SettingsTitleLayer()
        # Layer order:
        # 1. Base background (z_index 0)
        # 2. Background art (z_index 100)
        # 3. Global effects (z_index 300, if any)
        # 4. Menu (z_index 400)
        # 5. Title (z_index 500)
        self.layers = [self.base_layer, self.background_layer, self.menu_layer, self.title_layer]

    def handle_input(self, key):
        result = self.menu_layer.handle_key(key)
        if result is not None:
            return result
        if key in (ord('q'), ord('Q'), 27):
            return "QUIT"
        return None