# FileName: curses_scene_file_select.py
# version: 1.0
#
# Summary: Provides a unified file-list UI for both "load" mode and "save" mode.
#          Allows arrow-key navigation, file deletion, "Generate new map" (load mode),
#          or typed selection / "new file" (save mode).
#
# Tags: file, selection, curses

import curses
import debug

from .curses_common import draw_screen_frame, draw_title, draw_instructions
from .curses_animations import _draw_art
from .curses_art_skins import CROCODILE
from .curses_utils import safe_addstr, get_color_attr
from .curses_highlight import draw_global_selector_line

from map_list_logic import get_map_list, delete_map_file

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

def select_map_file(stdscr, mode='load'):
    """
    Displays a list of .json map files in 'maps' directory. Behavior depends on mode:

    mode='load':
      - Arrow keys move selection, Enter confirms.
      - Files are listed plus a top 'Generate new map' entry.
      - 'd' deletes the currently selected file (except the "Generate" slot).
      - 'q' or 'y' cancels, returning "".
      - 'v' toggles debug mode.
      - 'e' returns ("EDIT_GENERATE", None) if "Generate" is selected,
        or ("EDIT", <filename>) if a file is selected.
      - If user ENTERs on "Generate," returns "GENERATE".
      - Otherwise returns the chosen file name.

    mode='save':
      - Simple typed approach: user sees list (1..N) and can type a number or 'n' or Enter.
      - 'n' => returns "NEW_FILE".
      - An integer => overwrites the chosen file.
      - Enter with no input => cancels => returns "".
      - 'v' toggles debug mode.

    Returns a string (e.g. "GENERATE", "NEW_FILE", filename, or "")
    or possibly a tuple ("EDIT_GENERATE", None) or ("EDIT", filename).
    """
    files = get_map_list(maps_dir="maps", extension=".json")

    if mode == 'load':
        return _select_map_file_load_mode(stdscr, files)
    else:
        return _select_map_file_save_mode(stdscr, files)

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

def _select_map_file_save_mode(stdscr, files):
    while True:
        _draw_save_map_screen(stdscr)
        max_h, max_w = stdscr.getmaxyx()
        row = 10

        attr_cyan = get_color_attr("UI_CYAN")
        attr_yellow = get_color_attr("YELLOW_TEXT")

        if files:
            safe_addstr(stdscr, row, 2,
                "Maps (pick number to overwrite) or 'n' for new, or Enter to cancel:",
                attr_cyan, clip_borders=True)
            row += 1

            for i, filename in enumerate(files, start=1):
                if row >= max_h - 1:
                    break
                safe_addstr(stdscr, row, 2, f"{i}. {filename}", attr_yellow, clip_borders=True)
                row += 1

            if row < max_h - 1:
                safe_addstr(stdscr, row, 2,
                    "Enter choice or press Enter to cancel:",
                    attr_cyan, clip_borders=True)
                row += 1
        else:
            safe_addstr(stdscr, row, 2,
                "No existing maps. Press 'n' to create new, 'v' toggles debug, or Enter to cancel:",
                attr_cyan, clip_borders=True)
            row += 1

        stdscr.refresh()

        stdscr.nodelay(False)
        curses.curs_set(1)
        curses.echo()

        if row < max_h:
            try:
                selection_bytes = stdscr.getstr(row, 2, 20)
                if not selection_bytes:
                    # user just pressed Enter with no input
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

def _draw_save_map_screen(stdscr):
    stdscr.clear()
    stdscr.nodelay(False)
    stdscr.keypad(True)
    curses.curs_set(0)
    draw_screen_frame(stdscr)
    draw_title(stdscr, "Save Map", row=1)
    _draw_art(stdscr, CROCODILE, start_row=3, start_col=2)

    instructions = [
        "Select a map to overwrite, 'n'=new, ENTER=cancel, 'v'=toggle debug"
    ]
    draw_instructions(stdscr, instructions, from_bottom=3, color_name="WHITE_TEXT")

def _restore_input_mode(stdscr):
    curses.noecho()
    curses.curs_set(0)
    curses.napms(50)
    curses.flushinp()
    stdscr.nodelay(True)
