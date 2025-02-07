# File: curses_scene_load.py
# version: 2.3
#
# Summary:
#   Defines LoadScene – a plugin‑based scene for loading or generating a map.
#   The scene now uses layered drawing:
#       - Base background (lowest) for clearing/filling the screen.
#       - Background art (frame and theme art) above the base.
#       - Global rain effect (z_index=300, from global_effects_manager)
#       - Map list (z_index=400)
#       - Header (title and instructions, z_index=500)
#
# Tags: map, load, scene

import curses
import debug
from .scene_base import Scene
from .scene_layer_base import SceneLayer
from .curses_common import draw_screen_frame, draw_title, draw_instructions, _draw_art
from .where_curses_themes_lives import CURRENT_THEME
from .curses_utils import safe_addstr, get_color_attr
from .curses_selector_highlight import draw_global_selector_line

from map_system.map_list_logic import get_map_list, delete_map_file

def _restore_input_mode(stdscr):
    curses.noecho()
    curses.curs_set(0)
    curses.napms(50)
    curses.flushinp()
    stdscr.nodelay(True)

def prompt_delete_confirmation(stdscr, filename):
    max_h, max_w = stdscr.getmaxyx()
    question = f"Delete '{filename}'? (y/n)"
    attr = get_color_attr(CURRENT_THEME["confirmation_color"])

    row = max_h - 2
    blank_line = " " * (max_w - 4)
    safe_addstr(stdscr, row, 2, blank_line, attr, clip_borders=False)
    safe_addstr(stdscr, row, 2, question, attr, clip_borders=False)
    stdscr.refresh()

    stdscr.nodelay(False)
    curses.curs_set(1)
    curses.echo()

    while True:
        c = stdscr.getch()
        if c in (ord('y'), ord('Y')):
            _restore_input_mode(stdscr)
            return True
        elif c in (ord('n'), ord('N'), ord('q'), 27):
            _restore_input_mode(stdscr)
            return False

def _draw_load_background_art(stdscr):
    stdscr.keypad(True)
    curses.curs_set(0)
    draw_screen_frame(stdscr)
    crocodile_lines = CURRENT_THEME.get("crocodile_art", [])
    _draw_art(stdscr, crocodile_lines, start_row=3, start_col=2)

class LoadBaseLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="load_base", z_index=0)
      
    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        # Clear the screen (base background)
        stdscr.erase()

class LoadBackgroundLayer(SceneLayer):
    def __init__(self):
        # Background art layer above the base.
        super().__init__(name="load_background", z_index=100)
      
    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        _draw_load_background_art(stdscr)

class LoadHeaderLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="load_header", z_index=500)
      
    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        draw_title(stdscr, "Load Map", row=1)
        instructions = [
            "↑/↓ = select, ENTER = load, 'd' = del, 'q' = back, 'v' = dbg"
        ]
        draw_instructions(stdscr, instructions, from_bottom=3)

class LoadMenuLayer(SceneLayer):
    def __init__(self):
        # Map list layer.
        super().__init__(name="load_menu", z_index=400)
        self.options = ["Generate a new map"]
        # Now uses the default maps directory defined in map_list_logic.py
        maps = get_map_list(extension=".json")
        self.options.extend(maps)
        self.current_index = 0
        self.frame_count = 0

    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        max_h, max_w = stdscr.getmaxyx()
        row = 10  # Start drawing the options at row 10.
        for i, option in enumerate(self.options):
            display_text = option if i == 0 else f"{i}) {option}"
            is_selected = (i == self.current_index)
            draw_global_selector_line(
                stdscr,
                row,
                f"> {display_text}" if is_selected else f"  {display_text}",
                is_selected=is_selected,
                frame=self.frame_count
            )
            row += 1
        self.frame_count += 1

    def handle_key(self, key, stdscr):
        if key in (curses.KEY_UP, ord('w'), ord('W')):
            self.current_index = max(0, self.current_index - 1)
        elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
            self.current_index = min(len(self.options) - 1, self.current_index + 1)
        elif key in (curses.KEY_ENTER, 10, 13, 32):
            if self.current_index == 0:
                return "GENERATE"
            else:
                return self.options[self.current_index]
        elif key in (ord('q'), ord('Q'), 27):
            return ""  # Cancel and return to main menu.
        elif key in (ord('v'), ord('V')):
            debug.toggle_debug()
        elif key in (ord('d'), ord('D')):
            if self.current_index > 0:
                to_delete = self.options[self.current_index]
                confirm = prompt_delete_confirmation(stdscr, to_delete)
                if confirm:
                    success = delete_map_file(to_delete)
                    if success:
                        del self.options[self.current_index]
                        if self.current_index >= len(self.options):
                            self.current_index = len(self.options) - 1
        elif ord('0') <= key <= ord('9'):
            typed = key - ord('0')
            if 0 <= typed < len(self.options):
                self.current_index = typed
        return None

class LoadScene(Scene):
    def __init__(self):
        super().__init__()
        self.base_layer = LoadBaseLayer()
        self.bg_layer = LoadBackgroundLayer()
        self.menu_layer = LoadMenuLayer()
        self.header_layer = LoadHeaderLayer()
        # Layer order:
        # 1. Base background (z_index 0)
        # 2. Background art (z_index 100)
        # 3. Global rain effect (z_index 300, from global_effects_manager)
        # 4. Map list (z_index 400)
        # 5. Header (z_index 500)
        self.layers = [self.base_layer, self.bg_layer, self.menu_layer, self.header_layer]

    def handle_input(self, key):
        stdscr = self._get_stdscr()
        result = self.menu_layer.handle_key(key, stdscr)
        if result is not None:
            return result
        return None

    def _get_stdscr(self):
        return curses.initscr()