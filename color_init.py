# FileName: color_init.py
# version: 2.0
# Summary: Initializes curses color pairs and sets up global color mappings for all rendered text.
# Tags: colors, curses, setup

import curses
from color_defs import ALL_COLOR_DEFINITIONS, COLOR_PAIR_NAMES

# We'll store color pair IDs in a dictionary for easy lookup
color_pairs = {}

def init_colors():
    """
    Initialize all color pairs needed by the entire game.
    Loads definitions from color_definitions.py
    """
    curses.start_color()
    curses.use_default_colors()

    # Use the numeric definitions to actually init the color pairs in curses
    for (pair_index, fg, bg) in ALL_COLOR_DEFINITIONS:
        curses.init_pair(pair_index, fg, bg)

    # Then store them in color_pairs so code can do color_pairs["ROCK"], etc.
    color_pairs.update(COLOR_PAIR_NAMES)