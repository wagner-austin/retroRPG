# FileName: curses_scene_save.py
# version: 1.2 (updated)
#
# Summary: Extracted save-scene logic from curses_map_ui, now using a unified
#          "select_map_file(..., mode='save')" approach for listing and overwriting.
#
# Tags: map, save, scene

import curses
import debug

import map_io_main
from map_io_storage import save_map_file
from map_list_logic import file_exists_in_maps_dir
from .curses_scene_file_select import select_map_file
from .curses_utils import safe_addstr, get_color_attr

def prompt_for_filename(stdscr, prompt):
    """
    Prompt user for a filename (used by the save flow).
    """
    max_h, max_w = stdscr.getmaxyx()

    curses.echo()
    curses.curs_set(1)
    stdscr.nodelay(False)

    row = 10
    if row < max_h - 1:
        attr = get_color_attr("UI_CYAN")
        safe_addstr(stdscr, row, 2, prompt, attr, clip_borders=True)
        stdscr.refresh()

        filename_bytes = stdscr.getstr(row, 2 + len(prompt) + 1, 20)

        _restore_input_mode(stdscr)

        if filename_bytes:
            return filename_bytes.decode('utf-8', errors='ignore').strip()

    _restore_input_mode(stdscr)
    return ""

def save_map_ui (stdscr, placed_scenery, player=None,
                world_width=100, world_height=100,
                filename_override=None, notify_overwrite=False):
    """
    The user flow for saving a map. Potentially prompts for a filename,
    or overwriting an existing file.
    """
    if filename_override:
        filename = filename_override
    else:
        overwrite_or_new = select_map_file(stdscr, mode='save')
        if not overwrite_or_new:
            # user canceled => return
            return
        if overwrite_or_new == "NEW_FILE":
            filename = prompt_for_filename(stdscr, "Enter filename to save as: ")
            if not filename:
                return
            if not filename.endswith(".json"):
                filename += ".json"
        else:
            filename = overwrite_or_new

    file_existed = file_exists_in_maps_dir(filename)

    # Build the map data
    map_data = map_io_main.build_map_data(
        placed_scenery,
        player=player,
        world_width=world_width,
        world_height=world_height
    )

    # Actually save to disk
    save_map_file(f"maps/{filename}", map_data)

    # If we overwrote an existing file and want a brief pause/notification:
    if file_existed and notify_overwrite:
        curses.napms(500)

def _restore_input_mode(stdscr):
    curses.noecho()
    curses.curs_set(0)
    curses.napms(50)
    curses.flushinp()
    stdscr.nodelay(True)