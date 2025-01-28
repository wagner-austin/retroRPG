# FileName: map_io_ui.py
# version: 2.0
# Summary: Contains curses-based UI routines (map list, save prompts, load prompts, etc.)
#          for user map selection and generation. Also includes map loading/saving calls
#          that interact with the user.
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


def draw_load_map_screen(stdscr):
    stdscr.clear()
    stdscr.nodelay(False)
    stdscr.keypad(True)
    curses.curs_set(0)

    draw_screen_frame(stdscr)
    draw_title(stdscr, "Load Map", row=1)
    draw_art(stdscr, CROCODILE, start_row=3, start_col=2, color_name="ASCII_ART")
    instructions = [
        "↑/↓ = select, ENTER=load, 'e' = edit, 'd'=del, 'q'=back, 'v'=toggle debug"
    ]
    draw_instructions(stdscr, instructions, from_bottom=3, color_name="UI_YELLOW")
    stdscr.refresh()


def draw_save_map_screen(stdscr):
    stdscr.clear()
    stdscr.nodelay(False)
    stdscr.keypad(True)
    curses.curs_set(0)

    draw_screen_frame(stdscr)
    draw_title(stdscr, "Save Map", row=1)
    draw_art(stdscr, CROCODILE, start_row=3, start_col=2, color_name="ASCII_ART")
    instructions = [
        "Select a map to overwrite, 'n'=new, 'q'=cancel, 'v'=toggle debug"
    ]
    draw_instructions(stdscr, instructions, from_bottom=3, color_name="UI_YELLOW")
    stdscr.refresh()


def prompt_for_filename(stdscr, prompt):
    """
    Show 'prompt', let user type a filename (up to 20 chars).
    Returns the typed string or "" if canceled.
    """
    init_colors()
    draw_save_map_screen(stdscr)

    max_h, max_w = stdscr.getmaxyx()
    row = 10
    if row < max_h - 1:
        stdscr.addstr(row, 2, prompt, curses.color_pair(color_pairs["UI_CYAN"]))
        stdscr.refresh()
        curses.echo()
        filename_bytes = stdscr.getstr(row, 2 + len(prompt) + 1, 20)
        curses.noecho()
        if filename_bytes:
            return filename_bytes.decode('utf-8', errors='ignore').strip()
    return ""


def display_map_list(stdscr):
    """
    Shows a list of maps plus a top "Generate a new map"
    - Index 0 => "Generate a new map"
    - ...
    - 'q' => cancel => returns ""
    - 'e' => Editor mode
    - 'v' => toggle debug
    """
    init_colors()
    maps_dir = "maps"
    if not os.path.isdir(maps_dir):
        os.makedirs(maps_dir, exist_ok=True)

    files = [f for f in os.listdir(maps_dir) if f.endswith(".json")]
    files.sort()
    files.insert(0, "0) Generate a new map>")

    draw_load_map_screen(stdscr)
    max_h, max_w = stdscr.getmaxyx()
    selected_index = 0

    while True:
        draw_load_map_screen(stdscr)
        row = 10
        for i, fname in enumerate(files):
            if row >= max_h - 2:
                break
            display_text = f"{i}) {fname}" if i > 0 else "Generate a new map"
            if i == selected_index:
                try:
                    stdscr.addstr(
                        row, 2,
                        f"> {display_text}",
                        curses.color_pair(color_pairs["UI_YELLOW"]) | curses.A_REVERSE
                    )
                except:
                    pass
            else:
                try:
                    stdscr.addstr(
                        row, 2,
                        f"  {display_text}",
                        curses.color_pair(color_pairs["UI_YELLOW"])
                    )
                except:
                    pass
            row += 1

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_index = max(0, selected_index - 1)
        elif key == curses.KEY_DOWN:
            selected_index = min(len(files) - 1, selected_index + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            if selected_index == 0:
                return "GENERATE"
            else:
                return files[selected_index]
        elif key in (ord('q'), ord('y')):
            return ""
        elif key == ord('e'):
            # 'Edit' flow
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


def display_map_list_for_save(stdscr):
    """
    Shows a list of existing maps to overwrite OR create new with 'n'.
    Returns:
      - "NEW_FILE"
      - "" if canceled
      - or a filename to overwrite
    """
    init_colors()
    maps_dir = "maps"
    if not os.path.isdir(maps_dir):
        os.makedirs(maps_dir, exist_ok=True)

    files = [f for f in os.listdir(maps_dir) if f.endswith(".json")]
    files.sort()

    while True:
        draw_save_map_screen(stdscr)

        row = 10
        max_h, max_w = stdscr.getmaxyx()

        if files:
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
        # Loop again if invalid input


def load_map_ui(stdscr):
    """
    Prompts the user (via curses) to select or generate a map.
    Returns:
      - "" if canceled
      - a dict if "GENERATE" was chosen (the new map data)
      - ("EDIT_GENERATE", data) if user chooses to generate then edit
      - ("EDIT", filename) if user picks an existing map for editing
      - or a string filename if user picks an existing map to play
    """
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
                filename_override=None):
    """
    Prompts user to select a map file to overwrite or create a new file (unless 'filename_override' is given),
    then saves the current map data (including optional player coords) to JSON.
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

    map_data = map_io_main.build_map_data(
        placed_scenery,
        player=player,
        world_width=world_width,
        world_height=world_height
    )

    save_path = os.path.join(maps_dir, filename)
    save_map_file(save_path, map_data)


def ask_save_generated_map_ui(stdscr, placed_scenery, world_width, world_height, player=None):
    """
    Displays a minimal yes/no prompt on the existing screen (no clear).
    If 'y', calls save_map_ui. Otherwise skip saving.
    """
    max_h, max_w = stdscr.getmaxyx()
    prompt = "Save this generated map? (y/n)"

    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    row = max_h - 2
    col = 2

    try:
        stdscr.addstr(row, col, prompt, curses.A_BOLD)
    except:
        pass
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key in (ord('y'), ord('Y')):
            save_map_ui(stdscr, placed_scenery, player,
                        world_width=world_width,
                        world_height=world_height)
            break
        elif key in (ord('n'), ord('N'), ord('q'), 27):  # ESC
            break

    # Clean up the prompt
    try:
        stdscr.addstr(row, col, " " * len(prompt))
        stdscr.refresh()
    except:
        pass