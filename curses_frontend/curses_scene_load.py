# FileName: curses_scene_load.py
# version: 1.3 (extracted load UI from curses_scene_file_select.py)
#
# Summary: Contains the user flow for loading or generating a map.
#          Now calls the local function select_map_file_load_mode(...) 
#          for the file-list logic, instead of referencing curses_scene_file_select.
#
# Tags: map, load, scene

import curses
import debug

from procedural_map_generator.generator import generate_procedural_map
from .curses_common import draw_screen_frame, draw_title, draw_instructions
from .curses_animations import _draw_art
from .curses_art_skins import CROCODILE
from .curses_utils import safe_addstr, get_color_attr
from .curses_highlight import draw_global_selector_line

from map_list_logic import get_map_list, delete_map_file

def load_scene_ui(stdscr):
    """
    The user flow for loading a map or generating a new one.
    Returns either:
      - "" if canceled,
      - a dict (procedurally generated) if user picks "Generate a new map",
      - a tuple like ("EDIT", filename) or ("EDIT_GENERATE", data),
      - or just the filename string if user loads an existing map.
    """
    while True:
        selection = select_map_file_load_mode(stdscr)
        if not selection:
            # user canceled => back to main menu
            return ""

        if selection == "GENERATE":
            # user wants to generate a new map
            data = generate_procedural_map()
            return data

        if isinstance(selection, tuple):
            # The "EDITOR" variants
            action_type, actual_map = selection
            if action_type == "EDIT_GENERATE":
                data = generate_procedural_map()
                return (action_type, data)
            elif action_type == "EDIT":
                return (action_type, actual_map)

        elif isinstance(selection, dict):
            # If for some reason it returned a dict, just return it
            return selection

        else:
            # user picked an existing file by name
            return selection


def select_map_file_load_mode(stdscr):
    """
    Displays a list of .json map files in 'maps' directory for load usage.
    Returns "GENERATE", a filename string, "", or a tuple like ("EDIT", filename),
    or ("EDIT_GENERATE", None).
    """
    files = get_map_list(maps_dir="maps", extension=".json")
    return _select_map_file_load_mode(stdscr, files)


def _select_map_file_load_mode(stdscr, files):
    # Insert "Generate a new map>" at index 0
    files.insert(0, "0) Generate a new map>")

    selected_index = 0
    frame_count = 0

    while True:
        _draw_load_map_screen(stdscr)
        max_h, max_w = stdscr.getmaxyx()
        row = 10

        # Display the list of maps
        for i, fname in enumerate(files):
            if row >= max_h - 2:
                break

            if i == 0:
                display_text = "Generate a new map"
            else:
                display_text = f"{i}) {fname}"

            is_sel = (i == selected_index)
            draw_global_selector_line(
                stdscr,
                row,
                f"> {display_text}" if is_sel else f"  {display_text}",
                is_selected=is_sel,
                frame=frame_count
            )
            row += 1

        stdscr.refresh()
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord('w'), ord('W')):
            selected_index = max(0, selected_index - 1)
        elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
            selected_index = min(len(files) - 1, selected_index + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            # Enter = pick
            if selected_index == 0:
                return "GENERATE"
            else:
                return files[selected_index]
        elif key in (ord('q'), ord('y')):
            return ""
        elif key == ord('v'):
            debug.toggle_debug()
        elif key == ord('d'):
            # Deleting a file only if selected_index > 0
            if selected_index > 0:
                to_delete = files[selected_index]
                confirm = prompt_delete_confirmation(stdscr, to_delete)
                if confirm:
                    success = delete_map_file(to_delete, maps_dir="maps")
                    if success:
                        del files[selected_index]
                        if selected_index >= len(files):
                            selected_index = len(files) - 1
        elif key == ord('e'):
            # Editor mode
            if selected_index == 0:
                return ("EDIT_GENERATE", None)
            else:
                return ("EDIT", files[selected_index])
        elif ord('0') <= key <= ord('9'):
            # Quick numeric selection
            typed = key - ord('0')
            if 0 <= typed < len(files):
                selected_index = typed

        if len(files) == 1:
            # Only "Generate a new map" remains
            selected_index = 0

        frame_count += 1


def prompt_delete_confirmation(stdscr, filename):
    """
    Prompt the user: 'Delete X? (y/n)'. Return True if 'y', else False.
    """
    max_h, max_w = stdscr.getmaxyx()
    question = f"Delete '{filename}'? (y/n)"
    attr = get_color_attr("WHITE_TEXT")

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


def _draw_load_map_screen(stdscr):
    stdscr.clear()
    stdscr.nodelay(False)
    stdscr.keypad(True)
    curses.curs_set(0)
    draw_screen_frame(stdscr)
    draw_title(stdscr, "Load Map", row=1)
    _draw_art(stdscr, CROCODILE, start_row=3, start_col=2)

    instructions = [
        "↑/↓ = select, ENTER=load, 'd'=del, 'q'=back, 'v'=dbg, 'e'=editor"
    ]
    draw_instructions(stdscr, instructions, from_bottom=3, color_name="WHITE_TEXT")


def _restore_input_mode(stdscr):
    curses.noecho()
    curses.curs_set(0)
    curses.napms(50)
    curses.flushinp()
    stdscr.nodelay(True)