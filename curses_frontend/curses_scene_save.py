# File: curses_scene_save.py
# version: 2.0
#
# Summary:
#   Contains all save‑scene UI flows for picking/creating filenames,
#   prompting for overwrites, and calling the logic to store map data.
#   Now implemented as a plugin‑based scene similar to Home, Load, and Settings.
#
#   Transitions are no longer handled inside this module; instead, the flow manager
#   handles transitions when returning from the save scene.
#
# Tags: map, save, scene

import curses
import debug
from map_system.map_list_logic import get_map_list
from .curses_utils import safe_addstr, get_color_attr
from .curses_common import draw_screen_frame, draw_title, draw_instructions, _draw_art
from .where_curses_themes_lives import CURRENT_THEME
from scene_save_logic import (
    save_player_data,
    does_file_exist_in_maps_dir,
    build_and_save_map,
    update_player_coords_in_map
)
from .scene_base import Scene
from .scene_layer_base import SceneLayer
from .curses_game_renderer import CursesGameRenderer

# ---------------------------------------------------------------------
# Plugin Layers for the Save Scene
# ---------------------------------------------------------------------

class SaveBaseLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="save_base", z_index=0)
    def draw(self, renderer, dt, context):
        renderer.stdscr.erase()

class SaveBackgroundLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="save_background", z_index=100)
    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        draw_screen_frame(stdscr)
        crocodile_lines = CURRENT_THEME.get("crocodile_art", [])
        _draw_art(stdscr, crocodile_lines, start_row=3, start_col=2)

class SaveHeaderLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="save_header", z_index=500)
    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        draw_title(stdscr, "Save Map", row=1)
        instructions = ["Select a map to overwrite, 'n' for new, ENTER to cancel, 'v' toggles debug"]
        draw_instructions(stdscr, instructions, from_bottom=3)

class SaveMenuLayer(SceneLayer):
    def __init__(self, files):
        super().__init__(name="save_menu", z_index=400)
        self.files = files
        self.current_index = 0
    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        max_h, max_w = stdscr.getmaxyx()
        row = 10
        attr_prompt = get_color_attr(CURRENT_THEME["prompt_color"])
        attr_menu_item = get_color_attr(CURRENT_THEME["menu_item_color"])
        if self.files:
            safe_addstr(stdscr, row, 2, "Maps (pick number to overwrite) or 'n' for new, or ENTER to cancel:", attr_prompt, clip_borders=True)
            row += 1
            for i, filename in enumerate(self.files, start=1):
                indicator = ">" if (i-1) == self.current_index else " "
                safe_addstr(stdscr, row, 2, f"{indicator} {i}. {filename}", attr_menu_item, clip_borders=True)
                row += 1
            safe_addstr(stdscr, row, 2, "Enter choice or press ENTER to cancel:", attr_prompt, clip_borders=True)
        else:
            safe_addstr(stdscr, row, 2, "No existing maps. Press 'n' for new, 'v' toggles debug, or ENTER to cancel:", attr_prompt, clip_borders=True)
    def handle_key(self, key):
        if key in (curses.KEY_UP, ord('w'), ord('W')):
            self.current_index = max(0, self.current_index - 1)
        elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
            self.current_index = min(len(self.files) - 1, self.current_index + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            if self.files:
                return self.files[self.current_index]
            else:
                return ""
        elif key in (ord('n'), ord('N')):
            return "NEW_FILE"
        elif key in (ord('v'), ord('V')):
            debug.toggle_debug()
        elif ord('0') <= key <= ord('9'):
            digit = key - ord('0')
            if 1 <= digit <= len(self.files):
                return self.files[digit - 1]
        return None

class SaveScene(Scene):
    """
    Plugin-based scene for saving maps.
    Returns a filename (string) if an existing file is selected,
    "NEW_FILE" if the user chooses to create a new file,
    or an empty string if cancelled.
    """
    def __init__(self):
        super().__init__()
        files = get_map_list(extension=".json")
        self.base_layer = SaveBaseLayer()
        self.background_layer = SaveBackgroundLayer()
        self.menu_layer = SaveMenuLayer(files)
        self.header_layer = SaveHeaderLayer()
        self.layers = [self.base_layer, self.background_layer, self.menu_layer, self.header_layer]
    def handle_input(self, key):
        result = self.menu_layer.handle_key(key)
        if result is not None:
            return result
        return None

def run_save_scene(stdscr):
    renderer = CursesGameRenderer(stdscr)
    dt = 0
    save_scene = SaveScene()
    while True:
        renderer.render_scene(save_scene, dt=dt, context=None)
        dt += 1
        key = stdscr.getch()
        if key != -1:
            result = save_scene.handle_input(key)
            if result is not None:
                return result

def prompt_for_filename(stdscr, prompt):
    max_h, max_w = stdscr.getmaxyx()
    curses.echo()
    curses.curs_set(1)
    stdscr.nodelay(False)
    row = 10
    if row < max_h - 1:
        attr = get_color_attr(CURRENT_THEME["prompt_color"])
        safe_addstr(stdscr, row, 2, prompt, attr, clip_borders=True)
        stdscr.refresh()
        filename_bytes = stdscr.getstr(row, 2 + len(prompt) + 1, 20)
        _restore_input_mode(stdscr)
        if filename_bytes:
            return filename_bytes.decode('utf-8', errors='ignore').strip()
    _restore_input_mode(stdscr)
    return ""

def _restore_input_mode(stdscr):
    curses.noecho()
    curses.curs_set(0)
    curses.napms(50)
    curses.flushinp()
    stdscr.nodelay(True)

def save_map_ui(stdscr,
                placed_scenery,
                player=None,
                world_width=100,
                world_height=100,
                filename_override=None,
                notify_overwrite=False):
    if filename_override:
        filename = filename_override
    else:
        overwrite_or_new = run_save_scene(stdscr)
        if not overwrite_or_new:
            return
        if overwrite_or_new == "NEW_FILE":
            filename = prompt_for_filename(stdscr, "Enter filename to save as: ")
            if not filename:
                return
            if not filename.endswith(".json"):
                filename += ".json"
        else:
            filename = overwrite_or_new

    file_existed = does_file_exist_in_maps_dir(filename)
    build_and_save_map(filename, placed_scenery, player, world_width, world_height)
    if file_existed and notify_overwrite:
        curses.napms(0)
    # NOTE: Transition from the save scene back to HomeScene is now handled by MenuFlowManager.
    
def handle_post_game_scene_save(stdscr, model):
    """
    Called after the player returns from the game scene.
    Determines whether to save a new map or update an existing one,
    then calls the save UI flow.
    """
    save_player_data(model.player)
    if model.loaded_map_filename is None:
        wants_save = prompt_yes_no_curses(stdscr, "Save new map? (y/n)")
        if wants_save:
            placed_scenery = getattr(model, 'placed_scenery', {})
            w = getattr(model, 'world_width', 100)
            h = getattr(model, 'world_height', 100)
            save_map_ui(
                stdscr,
                placed_scenery=placed_scenery,
                player=model.player,
                world_width=w,
                world_height=h,
                filename_override=None,
                notify_overwrite=False
            )
    else:
        update_player_coords_in_map(model.loaded_map_filename, model.player.x, model.player.y)
        placed_scenery = getattr(model, 'placed_scenery', {})
        w = getattr(model, 'world_width', 100)
        h = getattr(model, 'world_height', 100)
        save_map_ui(
            stdscr,
            placed_scenery=placed_scenery,
            player=model.player,
            world_width=w,
            world_height=h,
            filename_override=model.loaded_map_filename,
            notify_overwrite=False
        )

def prompt_yes_no_curses(stdscr, question):
    max_h, max_w = stdscr.getmaxyx()
    row = max_h - 2
    col = 2
    stdscr.nodelay(False)
    curses.curs_set(1)
    curses.echo(0)
    blank_line = " " * (max_w - 4)
    safe_addstr(stdscr, row, col, blank_line, 0, clip_borders=True)
    stdscr.move(row, col)
    safe_addstr(stdscr, row, col, question, 0, clip_borders=True)
    stdscr.refresh()
    while True:
        c = stdscr.getch()
        if c in (ord('y'), ord('Y')):
            _restore_input_mode(stdscr)
            return True
        else:
            _restore_input_mode(stdscr)
            return False

def perform_quick_save(model, renderer):
    if not renderer:
        return
    if not hasattr(renderer, "get_curses_window"):
        return
    ui_win = renderer.get_curses_window()
    if not ui_win:
        return
    player = model.player
    if model.loaded_map_filename:
        save_map_ui(
            ui_win,
            model.placed_scenery,
            player=player,
            world_width=model.world_width,
            world_height=model.world_height,
            filename_override=model.loaded_map_filename
        )
    else:
        save_map_ui(
            ui_win,
            model.placed_scenery,
            player=player,
            world_width=model.world_width,
            world_height=model.world_height,
            filename_override=None
        )
    model.full_redraw_needed = True

# Legacy (non-plugin) implementations have been commented out.