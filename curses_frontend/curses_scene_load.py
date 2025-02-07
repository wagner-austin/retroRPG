# FileName: curses_scene_load.py
# version: 1.6
#
# Summary: Contains the user flow for loading or generating a map.
#          Now "q" or ESC will exit the load scene (instead of 'y').
#
# Changelog:
#  - Reverted to returning the literal string "GENERATE" instead of 
#    generating the map here. The actual generation is now done in 
#    curses_menu_flow_manager.py via create_procedural_model.
#
# Tags: map, load, scene

import curses
import debug

# Removed direct call to generate_procedural_map here (see commented code).
from .curses_common import draw_screen_frame, draw_title, draw_instructions, _draw_art
from .where_curses_themes_lives import CURRENT_THEME
from .curses_utils import safe_addstr, get_color_attr
from .curses_selector_highlight import draw_global_selector_line

from map_list_logic import get_map_list, delete_map_file


def load_scene_ui(stdscr):
    """
    The user flow for loading a map or generating a new one.
    Returns either:
      - "" if canceled,
      - "GENERATE" if user picks 'Generate a new map>',
      - a dict if user picks some data dict,
      - or just the filename string if user loads an existing map.
    """
    while True:
        selection = select_map_file_load_mode(stdscr)
        if not selection:
            # user canceled => back to main menu
            return ""

        if selection == "GENERATE":
            # Instead of generating here, just return "GENERATE" 
            # so the menu flow can handle it using create_procedural_model.
            return "GENERATE"

            # -- OLD code (commented out) --
            # data = generate_procedural_map()
            # return data

        elif isinstance(selection, dict):
            return selection

        else:
            # user picked an existing file by name
            return selection


def select_map_file_load_mode(stdscr, files=None):
    """
    Displays a list of .json map files in 'maps' directory for load usage.
    Returns "GENERATE", a filename string, "", or a tuple like ("EDIT", filename).
    """
    if files is None:
        files = get_map_list(maps_dir="maps", extension=".json")

    return _select_map_file_load_mode(stdscr, files)


def _select_map_file_load_mode(stdscr, files):
    # Insert "Generate a new map>" at index 0
    files.insert(0, "Generate a new map>")

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
        elif key in (curses.KEY_ENTER, 10, 13, 32):
            # Enter = pick
            if selected_index == 0:
                return "GENERATE"
            else:
                return files[selected_index]
        elif key in (ord('q'), ord('Q'), 27):
            # 'q' or ESC => cancel load
            return ""
        elif key in (ord('v'), ord('V')):
            debug.toggle_debug()
        elif key in (ord('d'), ord('D')):
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


def _draw_load_map_screen(stdscr):
    stdscr.clear()
    stdscr.nodelay(False)
    stdscr.keypad(True)
    curses.curs_set(0)
    draw_screen_frame(stdscr)
    draw_title(stdscr, "Load Map", row=1)

    # Use the theme's crocodile art
    crocodile_lines = CURRENT_THEME["crocodile_art"]
    _draw_art(stdscr, crocodile_lines, start_row=3, start_col=2)

    instructions = [
        "↑/↓ = select, ENTER=load, 'd'=del, 'q'=back, 'v'=dbg, 'e'=editor"
    ]
    draw_instructions(stdscr, instructions, from_bottom=3)


def _restore_input_mode(stdscr):
    curses.noecho()
    curses.curs_set(0)
    curses.napms(50)
    curses.flushinp()
    stdscr.nodelay(True)