# FileName: curses_scene_save.py
# version: 1.7
#
# Summary: Contains all save-scene logic for picking/creating filenames,
#          prompting for overwrites, and storing map data.
#          Also now includes handle_post_game_scene_save() to unify
#          new/existing map saves after gameplay.
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
from curses_frontend.curses_controls_ui import prompt_yes_no


def handle_post_game_scene_save(stdscr, model):
    """
    Called after the player returns from the game scene.
    Decides whether it’s a new map or existing map, then prompts user
    to save the newly placed or edited scenery.

    Logic summary:
      - If model.loaded_map_filename is None => ask user: "Save new map? (y/n)"
        -> if yes => call save_map_ui(...) for a new file
      - If model.loaded_map_filename is set => update player's x,y in JSON,
        then ask "Save changes to existing map? (y/n)" => if yes => overwrite
    """
    from player_char_io import save_player

    # Always ensure we have the player's updated data
    save_player(model.player)

    # brand-new map => ask user to save under new file name
    if model.loaded_map_filename is None:
        wants_save = _prompt_save_new_map(stdscr)
        if wants_save:
            placed_scenery = getattr(model, 'placed_scenery', {})
            # The big fix: read world_width / world_height from the model
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
        # Existing map => update player's coords, then prompt to confirm saving changes
        _update_player_coords_in_map(model.loaded_map_filename, model.player.x, model.player.y)

        placed_scenery = getattr(model, 'placed_scenery', {})
        w = getattr(model, 'world_width', 100)
        h = getattr(model, 'world_height', 100)

        # (Optional) call save_map_ui once to do a "preliminary" save
        # but you can skip this if you only want to save after user says "y"
        save_map_ui(
            stdscr,
            placed_scenery=placed_scenery,
            player=model.player,
            world_width=w,
            world_height=h,
            filename_override=model.loaded_map_filename,
            notify_overwrite=False
        )

        changes_saved = prompt_yes_no(None, "Save changes to existing map? (y/n)")
        if changes_saved:
            # Overwrite again after they confirm
            save_map_ui(
                stdscr,
                placed_scenery=placed_scenery,
                player=model.player,
                world_width=w,
                world_height=h,
                filename_override=model.loaded_map_filename,
                notify_overwrite=False
            )


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
        curses.napms(0)  # you can change the duration as you like


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
    while True:
        _draw_save_map_screen(stdscr)
        max_h, max_w = stdscr.getmaxyx()
        row = 10

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

        if row < max_h:
            try:
                selection_bytes = stdscr.getstr(row, 2, 20)
                if not selection_bytes:
                    _restore_input_mode(stdscr)
                    return ""
                selection = selection_bytes.decode('utf-8').strip()
            except:
                _restore_input_mode(stdscr)
                return ""
        else:
            _restore_input_mode(stdscr)
            return ""

        _restore_input_mode(stdscr)

        if not selection:
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
        attr = get_color_attr(CURRENT_THEME["prompt_color"])
        safe_addstr(stdscr, row, 2, prompt, attr, clip_borders=True)
        stdscr.refresh()

        filename_bytes = stdscr.getstr(row, 2 + len(prompt) + 1, 20)
        _restore_input_mode(stdscr)

        if filename_bytes:
            return filename_bytes.decode('utf-8', errors='ignore').strip()

    _restore_input_mode(stdscr)
    return ""


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

    crocodile_lines = CURRENT_THEME["crocodile_art"]
    _draw_art(stdscr, crocodile_lines, start_row=3, start_col=2)

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


def _prompt_save_new_map(stdscr):
    """
    Displays "Save new map? (y/n)" at the bottom. 'y' => yes, anything else => no.
    Returns True if user picks 'y', else False.
    """
    max_h, max_w = stdscr.getmaxyx()
    question = "Save new map? (y/n)"
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
            # 'n' / ESC / q / anything => no
            _restore_input_mode(stdscr)
            return False


def _update_player_coords_in_map(filename, px, py):
    """
    Helper to store player's final x,y in an existing map JSON.
    If you want to store more (e.g. gold, wood, HP), add them here.
    """
    import os, json
    from map_io_storage import save_map_file

    maps_dir = "maps"
    map_path = os.path.join(maps_dir, filename)
    if not os.path.exists(map_path):
        return
    try:
        with open(map_path, "r") as f:
            data = json.load(f)

        data["player_x"] = px
        data["player_y"] = py

        save_map_file(map_path, data)
    except:
        pass
