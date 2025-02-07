# File: curses_scene_home.py
# version: 2.2 (refactored to plugin architecture with separated base background)
#
# Summary:
#   Defines HomeScene, which uses plugin layers for the base background,
#   background art, menu, and title.
#
# Tags: scene, home, menu

import curses
from .scene_base import Scene
from .scene_layer_base import SceneLayer
from .curses_common import draw_screen_frame, draw_title, _draw_art
from .curses_selector_highlight import draw_global_selector_line
from .where_curses_themes_lives import CURRENT_THEME

class HomeBaseLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="home_base", z_index=0)
    
    def draw(self, renderer, dt, context):
        # Clear the screen or fill with a base color.
        stdscr = renderer.stdscr
        stdscr.erase()
        # Optionally, set a background fill:
        # stdscr.bkgd(' ', curses.color_pair(0))

class HomeBackgroundLayer(SceneLayer):
    def __init__(self):
        # Background art layer above the base.
        super().__init__(name="home_background", z_index=100)

    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        draw_screen_frame(stdscr)
        # Legacy: Removed drawing the title here.
        # draw_title(stdscr, "Welcome to Retro RPG!", row=1)
        main_menu_lines = CURRENT_THEME.get("main_menu_art", [])
        _draw_art(stdscr, main_menu_lines, start_row=3, start_col=2)

class HomeTitleLayer(SceneLayer):
    def __init__(self):
        # Title layer drawn on top.
        super().__init__(name="home_title", z_index=500)

    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        draw_title(stdscr, "Welcome to Retro RPG!", row=1)

class HomeMenuLayer(SceneLayer):
    def __init__(self):
        # Menu layer (drawn above background art but below the title).
        super().__init__(name="home_menu", z_index=400)
        self.menu_lines = [
            "~~~~~~~~~",
            "1) Play",
            "2) Quit",
            "3) Settings",
            "~~~~~~~~~"
        ]
        self.current_select_slot = 0  # index into selectable menu items

    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        max_h, max_w = stdscr.getmaxyx()
        from_bottom = 2
        start_row = max_h - from_bottom - len(self.menu_lines)
        if start_row < 1:
            start_row = 1

        row = start_row
        selectable_indices = [1, 2, 3]  # assume lines 1-3 (after the decorative line) are selectable
        for i, line_text in enumerate(self.menu_lines):
            is_selected = False
            if i in selectable_indices:
                sel_index = selectable_indices.index(i)
                if sel_index == self.current_select_slot:
                    is_selected = True
            draw_global_selector_line(
                stdscr, row, line_text,
                is_selected=is_selected,
                frame=dt  # use dt as frame count for animation
            )
            row += 1

    def move_selection_up(self):
        self.current_select_slot = max(0, self.current_select_slot - 1)

    def move_selection_down(self):
        self.current_select_slot = min(2, self.current_select_slot + 1)  # for 3 choices

    def get_current_choice(self):
        if self.current_select_slot == 0:
            return 1  # "Play"
        elif self.current_select_slot == 1:
            return 2  # "Quit"
        else:
            return 3  # "Settings"

class HomeScene(Scene):
    def __init__(self):
        super().__init__()
        self.base_layer = HomeBaseLayer()
        self.bg_layer = HomeBackgroundLayer()
        self.menu_layer = HomeMenuLayer()
        self.title_layer = HomeTitleLayer()
        # Layer order:
        # 1. Base background (z_index 0)
        # 2. Background art (z_index 100)
        # 3. Global effects (z_index 300, added via the global_effects_manager)
        # 4. Menu (z_index 400)
        # 5. Title (z_index 500)
        self.layers = [self.base_layer, self.bg_layer, self.menu_layer, self.title_layer]

    def handle_input(self, key):
        if key in (curses.KEY_UP, ord('w')):
            self.menu_layer.move_selection_up()
        elif key in (curses.KEY_DOWN, ord('s')):
            self.menu_layer.move_selection_down()
        elif key in (curses.KEY_ENTER, 10, 13):
            return self.menu_layer.get_current_choice()
        elif key == ord('1'):
            return 1
        elif key == ord('2'):
            return 2
        elif key == ord('3'):
            return 3
        return None