# FileName: curses_scene_save.py
# version: 1.6
#
# Summary: Contains all save-scene logic for picking/creating filenames,
#          prompting for overwrites, and storing map data.
#
# Tags: map, save, scene

import curses
import debug

import map_io_main
from map_io_storage import save_map_file
from map_list_logic import file_exists_in_maps_dir, get_map_list
from .curses_utils import safe_addstr, get_color_attr
from .curses_common import draw_screen_frame, draw_title, draw_instructions
from .curses_animations import _draw_art
from .curses_themes import CURRENT_THEME


def select_map_file(stdscr, mode='save'):
    """
    Bridging function to display a file list for 'save' usage.

    - If mode != 'save', raises ValueError.
    - Fetches existing .json files from 'maps' dir,
      then calls select_map_file_save_mode(...).
    - Returns either the chosen filename, "NEW_FILE", or "" if canceled.
    """
    if mode != 'save':
        raise ValueError("select_map_file(...) now only supports 'save' mode.")

    files = get_map_list(maps_dir="maps", extension=".json")
    return select_map_file_save_mode(stdscr, files)


def select_map_file_save_mode(stdscr, files):
    """
    Displays a list of .json map files for 'save' usage.

    Returns one of:
      - "NEW_FILE": user wants to create a new filename
      - a filename string (chosen from the list)
      - "" if canceled
    """
    from .curses_themes import CURRENT_THEME

    while True:
        _draw_save_map_screen(stdscr)
        max_h, max_w = stdscr.getmaxyx()
        row = 10

        # Instead of hard-coded "UI_CYAN"/"YELLOW_TEXT", use the theme:
        attr_prompt = get_color_attr(CURRENT_THEME["prompt_color"])
        attr_menu_item = get_color_attr(CURRENT_THEME["menu_item_color"])

        if files:
            safe_addstr(
                stdscr, row, 2,
                "Maps (pick number to overwrite) or 'n' for new, or Enter to cancel:",
                attr_prompt, clip_borders=True
            )
            row += 1

            for i, filename in enumerate(files, start=1):
                if row >= max_h - 1:
                    break
                safe_addstr(stdscr, row, 2, f"{i}. {filename}", attr_menu_item, clip_borders=True)
                row += 1

            if row < max_h - 1:
                safe_addstr(
                    stdscr, row, 2,
                    "Enter choice or press Enter to cancel:",
                    attr_prompt, clip_borders=True
                )
                row += 1
        else:
            # No existing files found
            safe_addstr(
                stdscr, row, 2,
                "No existing maps. Press 'n' to create new, 'v' toggles debug, or Enter to cancel:",
                attr_prompt, clip_borders=True
            )
            row += 1

        stdscr.refresh()

        stdscr.nodelay(False)
        curses.curs_set(1)
        curses.echo()

        # Get user input on the same row (if we still have space)
        if row < max_h:
            try:
                selection_bytes = stdscr.getstr(row, 2, 20)
                if not selection_bytes:
                    # User pressed Enter with no input => canceled
                    _restore_input_mode(stdscr)
                    return ""
                selection = selection_bytes.decode('utf-8').strip()
            except:
                _restore_input_mode(stdscr)
                return ""
        else:
            _restore_input_mode(stdscr)
            return ""

        # Restore normal (no-echo) mode
        _restore_input_mode(stdscr)

        if not selection:
            # User canceled
            return ""
        if selection.lower() == 'n':
            return "NEW_FILE"
        elif selection.lower() == 'v':
            debug.toggle_debug()
            continue
        elif selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(files):
                return files[idx]


def prompt_for_filename(stdscr, prompt):
    """
    Prompt user for a new filename (used by the save flow).
    Returns the typed string or "" if canceled/empty.
    """
    max_h, max_w = stdscr.getmaxyx()

    curses.echo()
    curses.curs_set(1)
    stdscr.nodelay(False)

    row = 10
    if row < max_h - 1:
        # Use the theme's prompt_color for the prompt text
        from .curses_themes import CURRENT_THEME
        attr = get_color_attr(CURRENT_THEME["prompt_color"])

        safe_addstr(stdscr, row, 2, prompt, attr, clip_borders=True)
        stdscr.refresh()

        filename_bytes = stdscr.getstr(row, 2 + len(prompt) + 1, 20)
        _restore_input_mode(stdscr)

        if filename_bytes:
            return filename_bytes.decode('utf-8', errors='ignore').strip()

    # If user didn't enter anything or row is out of range:
    _restore_input_mode(stdscr)
    return ""


def save_map_ui(stdscr,
                placed_scenery,
                player=None,
                world_width=100,
                world_height=100,
                filename_override=None,
                notify_overwrite=False):
    """
    The user flow for saving a map. Potentially prompts for a filename or overwriting.
    If filename_override is given, skip the selection and use that name directly.
    Otherwise:
      1) Show a "save" list of existing files (via select_map_file(..., mode='save')).
      2) User can pick a file to overwrite or type 'n' for new => new filename prompt.
      3) If user cancels at any point, we just return.
    """
    if filename_override:
        # If we have a forced filename, skip the UI and use that
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

    # Check if the file already existed (so we can notify about overwriting)
    file_existed = file_exists_in_maps_dir(filename)

    # Build the map data from the given scenery/player
    map_data = map_io_main.build_map_data(
        placed_scenery,
        player=player,
        world_width=world_width,
        world_height=world_height
    )

    # Actually write the map data to disk
    save_map_file(f"maps/{filename}", map_data)

    # If we overwrote an existing file and want a brief pause:
    if file_existed and notify_overwrite:
        curses.napms(0)


def _draw_save_map_screen(stdscr):
    """
    Draws the "Save Map" header/art/instructions at the top.
    """
    stdscr.clear()
    stdscr.nodelay(False)
    stdscr.keypad(True)
    curses.curs_set(0)

    draw_screen_frame(stdscr)
    draw_title(stdscr, "Save Map", row=1)

    # Use the theme's crocodile art
    crocodile_lines = CURRENT_THEME["crocodile_art"]
    _draw_art(stdscr, crocodile_lines, start_row=3, start_col=2)

    # Let instructions default to CURRENT_THEME["instructions_color"]
    instructions = [
        "Select a map to overwrite, 'n'=new, ENTER=cancel, 'v'=toggle debug"
    ]
    draw_instructions(stdscr, instructions, from_bottom=3)


def _restore_input_mode(stdscr):
    """
    Helper to restore no-echo, no-delay mode after user input.
    """
    curses.noecho()
    curses.curs_set(0)
    curses.napms(50)
    curses.flushinp()
    stdscr.nodelay(True)