# FileName: color_library.py
# version: 1.0
# Summary: Defines base curses colors plus extended ones (light_gray, etc.).
# Tags: colors, config

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
# Only works if curses.can_change_color() == True on your terminal.
EXTENDED_COLORS = {
    "light_gray": 8,
    "dark_gray":  9,
    # Add more if desired: "bright_green":10, etc.
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