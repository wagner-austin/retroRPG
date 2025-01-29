# FileName: map_io_ui.py
# version: 2.11
# Summary: Contains curses-based UI routines (map list, save prompts, load prompts),
#          uses safe_addstr for clip_borders.
# Tags: map, ui, io

import curses
import os
import debug

from color_init import init_colors, color_pairs
from ui_main import (
    draw_screen_frame,
    draw_title,
    draw_art,
    draw_instructions
)
from art_main import CROCODILE
from highlight_selector import draw_global_selector_line
from curses_utils import safe_addstr, safe_addch, get_color_attr


def draw_load_map_screen(stdscr):
    stdscr.clear()
    stdscr.nodelay(False)
    stdscr.keypad(True)
    curses.curs_set(0)
    draw_screen_frame(stdscr)
    draw_title(stdscr, "Load Map", row=1)
    draw_art(stdscr, CROCODILE, start_row=3, start_col=2)

    # Instructions now white instead of magenta
    instructions = [
        "↑/↓ = select, ENTER=load, 'd'=del, 'q'=back, 'v'=toggle debug"
    ]
    draw_instructions(stdscr, instructions, from_bottom=3, color_name="WHITE_TEXT")


def draw_save_map_screen(stdscr):
    stdscr.clear()
    stdscr.nodelay(False)
    stdscr.keypad(True)
    curses.curs_set(0)
    draw_screen_frame(stdscr)
    draw_title(stdscr, "Save Map", row=1)
    draw_art(stdscr, CROCODILE, start_row=3, start_col=2)

    instructions = [
        "Select a map to overwrite, 'n'=new, 'ENTER'=cancel, 'v'=toggle debug"
    ]
    draw_instructions(stdscr, instructions, from_bottom=3, color_name="UI_MAGENTA")


def prompt_for_filename(stdscr, prompt):
    init_colors()
    draw_save_map_screen(stdscr)
    max_h, max_w = stdscr.getmaxyx()
    row = 10
    if row < max_h - 1:
        stdscr.refresh()
        attr = get_color_attr("UI_CYAN")
        safe_addstr(stdscr, row, 2, prompt, attr, clip_borders=True)
        stdscr.refresh()
        curses.echo()
        filename_bytes = stdscr.getstr(row, 2 + len(prompt) + 1, 20)
        curses.noecho()
        if filename_bytes:
            return filename_bytes.decode('utf-8', errors='ignore').strip()
    return ""


def _draw_global_text(stdscr, row, text, attr):
    safe_addstr(stdscr, row, 2, text, attr, clip_borders=True)


def prompt_delete_confirmation(stdscr, filename):
    """
    Prompt the user: "Delete <filename>? (y/n)"
    Return True if the user chooses 'y', otherwise False.
    """
    max_h, max_w = stdscr.getmaxyx()
    question = f"Delete '{filename}'? (y/n)"
    attr = get_color_attr("WHITE_TEXT")

    # We'll draw it on the bottom row or near it
    row = max_h - 2
    safe_addstr(stdscr, row, 2, " " * (max_w - 4), attr, clip_borders=False)
    safe_addstr(stdscr, row, 2, question, attr, clip_borders=False)
    stdscr.refresh()

    while True:
        c = stdscr.getch()
        if c in (ord('y'), ord('Y')):
            return True
        elif c in (ord('n'), ord('N'), ord('q'), 27):
            return False


def display_map_list(stdscr):
    init_colors()
    maps_dir = "maps"
    if not os.path.isdir(maps_dir):
        os.makedirs(maps_dir, exist_ok=True)

    files = [f for f in os.listdir(maps_dir) if f.endswith(".json")]
    files.sort()
    files.insert(0, "0) Generate a new map>")

    selected_index = 0
    frame_count = 0

    while True:
        draw_load_map_screen(stdscr)
        max_h, max_w = stdscr.getmaxyx()
        row = 10

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
            if selected_index == 0:
                return "GENERATE"
            else:
                return files[selected_index]
        elif key in (ord('q'), ord('y')):
            return ""
        elif key == ord('e'):
            # If user typed 'e', we interpret that as edit
            if selected_index == 0:
                return ("EDIT_GENERATE", None)
            else:
                return ("EDIT", files[selected_index])
        elif key == ord('v'):
            debug.toggle_debug()
        elif key == ord('d'):
            # Delete function
            if selected_index > 0:  # index 0 is "Generate a new map>", cannot be deleted
                to_delete = files[selected_index]
                confirm = prompt_delete_confirmation(stdscr, to_delete)
                if confirm:
                    try:
                        os.remove(os.path.join(maps_dir, to_delete))
                    except OSError:
                        pass
                    # remove from list
                    del files[selected_index]
                    if selected_index >= len(files):
                        selected_index = len(files) - 1
        elif ord('0') <= key <= ord('9'):
            typed = key - ord('0')
            if 0 <= typed < len(files):
                selected_index = typed

        if len(files) == 1:
            # If only one entry, it's "Generate a new map>", so keep selected_index=0
            selected_index = 0

        frame_count += 1


def display_map_list_for_save(stdscr):
    init_colors()
    maps_dir = "maps"
    if not os.path.isdir(maps_dir):
        os.makedirs(maps_dir, exist_ok=True)

    files = [f for f in os.listdir(maps_dir) if f.endswith(".json")]
    files.sort()

    while True:
        draw_save_map_screen(stdscr)
        max_h, max_w = stdscr.getmaxyx()
        row = 10

        if files:
            stdscr.refresh()
            try:
                attr_cyan = get_color_attr("UI_CYAN")
                _draw_global_text(
                    stdscr,
                    row,
                    "Maps (pick number to overwrite) or 'n' for new, 'v' toggles debug:",
                    attr_cyan
                )
            except:
                pass
            row += 1
            for i, filename in enumerate(files, start=1):
                if row >= max_h - 1:
                    break
                try:
                    attr_yellow = get_color_attr("YELLOW_TEXT")
                    _draw_global_text(stdscr, row, f"{i}. {filename}", attr_yellow)
                except:
                    pass
                row += 1
            if row < max_h - 1:
                try:
                    _draw_global_text(
                        stdscr,
                        row,
                        "Enter choice or press Enter to cancel:",
                        attr_cyan
                    )
                except:
                    pass
                row += 1
        else:
            stdscr.refresh()
            try:
                attr_cyan = get_color_attr("UI_CYAN")
                _draw_global_text(
                    stdscr,
                    row,
                    "No existing maps. Press 'n' to create new, 'v' toggles debug, or Enter to cancel:",
                    attr_cyan
                )
            except:
                pass
            row += 1

        stdscr.refresh()
        try:
            if row < max_h:
                selection_bytes = stdscr.getstr(row, 2, 20)
                if not selection_bytes:
                    return ""
                selection = selection_bytes.decode('utf-8').strip()
            else:
                return ""

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
        except:
            pass


def load_map_ui(stdscr):
    selection = display_map_list(stdscr)
    if not selection:
        return ""
    if selection == "GENERATE":
        from procedural_map_generator.generator import generate_procedural_map
        return generate_procedural_map()
    if isinstance(selection, tuple):
        if selection[0] == "EDIT_GENERATE":
            from procedural_map_generator.generator import generate_procedural_map
            data = generate_procedural_map()
            return ("EDIT_GENERATE", data)
        elif selection[0] == "EDIT":
            return ("EDIT", selection[1])
        return ""
    return selection


def save_map_ui(stdscr, placed_scenery, player=None,
                world_width=100, world_height=100,
                filename_override=None,
                notify_overwrite=False):
    import map_io_main
    from map_io_storage import save_map_file

    if filename_override:
        filename = filename_override
    else:
        overwrite_or_new = display_map_list_for_save(stdscr)
        if not overwrite_or_new:
            return  # user canceled
        if overwrite_or_new == "NEW_FILE":
            filename = prompt_for_filename(stdscr, "Enter filename to save as: ")
            if not filename:
                return
            if not filename.endswith(".json"):
                filename += ".json"
        else:
            filename = overwrite_or_new

    maps_dir = "maps"
    if not os.path.isdir(maps_dir):
        os.makedirs(maps_dir, exist_ok=True)

    save_path = os.path.join(maps_dir, filename)
    file_existed = os.path.exists(save_path)

    map_data = map_io_main.build_map_data(
        placed_scenery,
        player=player,
        world_width=world_width,
        world_height=world_height
    )

    save_map_file(save_path, map_data)

    if file_existed and notify_overwrite:
        curses.napms(500)

def ask_save_generated_map_ui(stdscr, placed_scenery, world_width, world_height, player=None):
    return