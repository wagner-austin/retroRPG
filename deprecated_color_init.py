# FileName: color_init.py
# version: 3.3
# Summary: Initializes curses color pairs. Skips invalid indexes if terminal supports fewer colors.
# Tags: colors, curses, setup

import curses

#
# MERGED DEFINITIONS (previously from color_library.py):
#

# The standard 8 curses colors mapped to friendly names:
BASE_COLORS = {
    "black":   curses.COLOR_BLACK,
    "red":     curses.COLOR_RED,
    "green":   curses.COLOR_GREEN,
    "yellow":  curses.COLOR_YELLOW,
    "blue":    curses.COLOR_BLUE,
    "magenta": curses.COLOR_MAGENTA,
    "cyan":    curses.COLOR_CYAN,
    "white":   curses.COLOR_WHITE,
}

# Extended color indexes for e.g. light_gray, dark_gray, etc.
EXTENDED_COLORS = {
    "light_gray": 8,
    "dark_gray":  9,
    # You could add more if desired: "bright_green":10, etc.
}

def define_extended_colors():
    """
    Attempt to initialize extra colors if the terminal supports color redefinition.
    Each init_color(index, r, g, b) has r,g,b from 0..1000.
    """
    if not curses.can_change_color():
        return

    # light_gray => ~70% white
    curses.init_color(8, 700, 700, 700)
    # dark_gray  => ~30% white
    curses.init_color(9, 300, 300, 300)


color_pairs = {}

def init_colors():
    curses.start_color()
    curses.use_default_colors()

    # Attempt to define extended colors if supported
    define_extended_colors()

    # Merge base + extended color definitions
    all_colors = dict(BASE_COLORS)
    all_colors.update(EXTENDED_COLORS)

    pair_index = 1
    for fg_name, fg_val in all_colors.items():
        for bg_name, bg_val in all_colors.items():
            # Only define pairs if fg_val & bg_val are within the supported range
            if fg_val < curses.COLORS and bg_val < curses.COLORS:
                pair_name = f"{fg_name}_on_{bg_name}"
                curses.init_pair(pair_index, fg_val, bg_val)
                color_pairs[pair_name] = pair_index
                pair_index += 1

    # Create alias names for legacy references
    ALIAS_MAP = {
        # Removed "UI_YELLOW": "yellow_on_black" to avoid duplication with "YELLOW_TEXT"
        "WHITE_TEXT":        "white_on_black",
        "UI_CYAN":           "cyan_on_black",
        "UI_MAGENTA":        "magenta_on_black",
        "UI_WHITE_ON_BLUE":  "white_on_blue",
        "YELLOW_TEXT":       "yellow_on_black",
        "ASCII_ART":         "white_on_black",
        "TREE_TOP":          "green_on_black",
        "ROCK":              "white_on_black",
        "RIVER":             "white_on_blue",
        "GRASS":             "white_on_green",
        "PATH":              "black_on_yellow",
        # Add more if needed
    }

    for alias_name, real_name in ALIAS_MAP.items():
        if real_name in color_pairs:
            color_pairs[alias_name] = color_pairs[real_name]
        else:
            # fallback to white_on_black if real_name not defined
            color_pairs[alias_name] = color_pairs.get("white_on_black", 0)