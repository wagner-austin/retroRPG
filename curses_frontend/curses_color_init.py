# FileName: curses_color_init.py
#
# version: 3.3
#
# Summary: Initializes curses color pairs. Skips invalid indexes if terminal supports fewer colors.
#
# Tags: colors, curses, setup

import curses

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
    # Could add more if terminal supports it.
}

def define_extended_colors():
    """Attempt to initialize extra colors if the terminal supports color redefinition."""
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

    # Merge base + extended colors
    all_colors = dict(BASE_COLORS)
    all_colors.update(EXTENDED_COLORS)

    pair_index = 1
    for fg_name, fg_val in all_colors.items():
        for bg_name, bg_val in all_colors.items():
            if fg_val < curses.COLORS and bg_val < curses.COLORS:
                pair_name = f"{fg_name}_on_{bg_name}"
                curses.init_pair(pair_index, fg_val, bg_val)
                color_pairs[pair_name] = pair_index
                pair_index += 1

    # Removed alias mapping in favor of a standardized naming system.