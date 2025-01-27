# FileName: map_io_ui.py
# version: 2.0 
# Contains all curses-based UI for listing maps, prompting filenames, etc.

import curses
import os

from color_init import init_colors, color_pairs
# We import general UI utilities from ui_main
from ui_main import (
    draw_screen_frame,  # CHANGED
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

    draw_screen_frame(stdscr)  # CHANGED: replaced draw_border
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

    draw_screen_frame(stdscr)  # CHANGED
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
    draw_save_map_screen(stdscr)  # Instead of draw_save_screen

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
        # Re-draw the load map screen each loop
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
        elif key == ord('q') or key == ord('y'):
            return ""
        elif key == ord('e'):
            if selected_index == 0:
                return ("EDIT_GENERATE", None)
            else:
                return ("EDIT", files[selected_index])
        elif key == ord('v'):
            import debug
            debug.toggle_debug()
            # Continue the loop so user sees changes immediately
        elif ord('0') <= key <= ord('9'):
            typed = key - ord('0')
            if 0 <= typed < len(files):
                selected_index = typed

        # If there's only one file, always stay at index=0
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
                stdscr.addstr(row, 2,
                              "No existing maps. Press 'n' to create new, 'v' toggles debug, or Enter to cancel:",
                              curses.color_pair(color_pairs["UI_CYAN"]))
            except:
                pass
            row += 1

        stdscr.refresh()

        # Single line input
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
                # After toggling, re-draw the screen and loop again
                continue
            elif selection.isdigit():
                idx = int(selection) - 1
                if 0 <= idx < len(files):
                    return files[idx]
        except:
            pass

        # If input doesn't match known options, loop back