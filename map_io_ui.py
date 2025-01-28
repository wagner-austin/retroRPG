# FileName: map_io_ui.py
# version: 2.7
# Summary: Contains curses-based UI routines (map list, save prompts, load prompts).
#          Now does no text on overwrite, just a 500ms nap if `notify_overwrite=True`.
# Tags: map, ui, io

import curses
import os

from color_init import init_colors, color_pairs
from ui_main import (
    draw_screen_frame,
    draw_title,
    draw_art,
    draw_instructions
)
from art_main import CROCODILE
from highlight_selector import draw_global_selector_line


def draw_load_map_screen(stdscr):
    stdscr.clear()
    stdscr.nodelay(False)
    stdscr.keypad(True)
    curses.curs_set(0)
    draw_screen_frame(stdscr)
    draw_title(stdscr, "Load Map", row=1)
    draw_art(stdscr, CROCODILE, start_row=3, start_col=2, color_name="ASCII_ART")

    instructions = [
        "↑/↓ = select, ENTER=load, 'd'=del, 'q'=back, 'v'=toggle debug"
    ]
    draw_instructions(stdscr, instructions, from_bottom=3, color_name="UI_YELLOW")


def draw_save_map_screen(stdscr):
    stdscr.clear()
    stdscr.nodelay(False)
    stdscr.keypad(True)
    curses.curs_set(0)
    draw_screen_frame(stdscr)
    draw_title(stdscr, "Save Map", row=1)
    draw_art(stdscr, CROCODILE, start_row=3, start_col=2, color_name="ASCII_ART")

    instructions = [
        "Select a map to overwrite, 'n'=new, 'ENTER'=cancel, 'v'=toggle debug"
    ]
    draw_instructions(stdscr, instructions, from_bottom=3, color_name="UI_YELLOW")


def prompt_for_filename(stdscr, prompt):
    init_colors()
    draw_save_map_screen(stdscr)
    max_h, max_w = stdscr.getmaxyx()
    row = 10
    if row < max_h - 1:
        stdscr.refresh()
        stdscr.addstr(row, 2, prompt, curses.color_pair(color_pairs["UI_CYAN"]))
        stdscr.refresh()
        curses.echo()
        filename_bytes = stdscr.getstr(row, 2 + len(prompt) + 1, 20)
        curses.noecho()
        if filename_bytes:
            return filename_bytes.decode('utf-8', errors='ignore').strip()
    return ""


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
            if selected_index == 0:
                return ("EDIT_GENERATE", None)
            else:
                return ("EDIT", files[selected_index])
        elif key == ord('v'):
            import debug
            debug.toggle_debug()
        elif ord('0') <= key <= ord('9'):
            typed = key - ord('0')
            if 0 <= typed < len(files):
                selected_index = typed

        if len(files) == 1:
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
                stdscr.addstr(
                    row, 2,
                    "Maps (pick number to overwrite) or 'n' for new, 'v' toggles debug:",
                    curses.color_pair(color_pairs["UI_CYAN"])
                )
            except:
                pass
            row += 1
            for i, filename in enumerate(files, start=1):
                if row >= max_h - 1:
                    break
                try:
                    stdscr.addstr(row, 2, f"{i}. {filename}",
                                  curses.color_pair(color_pairs["UI_YELLOW"]))
                except:
                    pass
                row += 1
            if row < max_h - 1:
                try:
                    stdscr.addstr(row, 2,
                                  "Enter choice or press Enter to cancel:",
                                  curses.color_pair(color_pairs["UI_CYAN"]))
                except:
                    pass
                row += 1
        else:
            stdscr.refresh()
            try:
                stdscr.addstr(
                    row, 2,
                    "No existing maps. Press 'n' to create new, 'v' toggles debug, or Enter to cancel:",
                    curses.color_pair(color_pairs["UI_CYAN"])
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
                import debug
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
    """
    notify_overwrite=True => if a file is being overwritten, do a 500ms nap (no text).
    notify_overwrite=False => skip any nap or notification.
    """
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

    # Actually save the file
    save_map_file(save_path, map_data)

    # if overwriting
    if file_existed and notify_overwrite:
        # just do a 500ms nap, no text
        curses.napms(500)
    # else no message or nap

def ask_save_generated_map_ui(stdscr, placed_scenery, world_width, world_height, player=None):
    """
    Disabled to avoid a second "save generated map?" prompt.
    """
    return