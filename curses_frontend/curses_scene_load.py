# FileName: curses_scene_load.py
# version: 1.2 (updated)
#
# Summary: Contains the user flow for loading or generating a map.
#          Now calls into the unified "select_map_file(..., mode='load')"
#          instead of duplicating file-list logic.
#
# Tags: map, load, scene

import curses
import debug

from procedural_map_generator.generator import generate_procedural_map
from .curses_scene_file_select import select_map_file

def load_map_ui(stdscr):
    """
    The user flow for loading a map or generating a new one.
    Returns either:
      - "" if canceled,
      - a dict (procedurally generated) if user picks "Generate a new map",
      - a tuple like ("EDIT", filename) or ("EDIT_GENERATE", data),
      - or just the filename string if user loads an existing map.
    """
    while True:
        selection = select_map_file(stdscr, mode='load')
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
                # generate fresh map, then return it as a tuple so caller knows
                data = generate_procedural_map()
                return (action_type, data)
            elif action_type == "EDIT":
                return selection  # ("EDIT", filename)

        elif isinstance(selection, dict):
            # If for some reason it returned a dict, just return it
            return selection

        else:
            # user picked an existing file by name
            return selection