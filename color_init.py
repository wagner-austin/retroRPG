# FileName: color_init.py
# version: 3.1
# Summary: Initializes curses color pairs. Skips invalid indexes if terminal supports fewer colors.
# Tags: colors, curses, setup

import curses
from color_library import BASE_COLORS, EXTENDED_COLORS, define_extended_colors

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
        "UI_YELLOW":    "yellow_on_black",
        "WHITE_TEXT":   "white_on_black",
        "UI_CYAN":      "cyan_on_black",
        "UI_MAGENTA":   "magenta_on_black",
        "UI_WHITE_ON_BLUE": "white_on_blue",
        "YELLOW_TEXT":  "yellow_on_black",
        "ASCII_ART":    "white_on_black",
        "TREE_TOP":     "green_on_black",
        "ROCK":         "white_on_black",
        "RIVER":        "white_on_blue",
        "GRASS":        "white_on_green",
        "PATH":         "black_on_yellow",
        # Add more if needed
    }

    for alias_name, real_name in ALIAS_MAP.items():
        if real_name in color_pairs:
            color_pairs[alias_name] = color_pairs[real_name]
        else:
            # fallback to white_on_black if real_name not defined
            color_pairs[alias_name] = color_pairs.get("white_on_black", 0)