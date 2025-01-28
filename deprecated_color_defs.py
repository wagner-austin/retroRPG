# FileName: color_defs.py
# version: 1.0
# Summary: Defines color constants or enums used throughout the game for consistent color referencing.
# Tags: colors, config

import curses

# Each tuple => (pair_index, foreground_color, background_color)
# Add or remove lines here to define new tile colors, UI colors, etc.
MAP_COLOR_DEFINITIONS = [
    (1, curses.COLOR_GREEN,   -1),  # Tree top
    (2, curses.COLOR_YELLOW,  -1),  # Bridge/trunk
    (3, curses.COLOR_WHITE,   -1),  # Rock
    (4, curses.COLOR_WHITE, curses.COLOR_BLUE),  # River
    (5, curses.COLOR_WHITE, curses.COLOR_GREEN), # Grass
    (6, curses.COLOR_WHITE,   -1),  # ASCII art
    (7, curses.COLOR_GREEN, curses.COLOR_WHITE), # Tree top hiding player
    (8, curses.COLOR_WHITE, curses.COLOR_YELLOW),# Path
    (9, curses.COLOR_WHITE,   -1),  # White text
    (10, curses.COLOR_BLACK, curses.COLOR_WHITE),# Flash highlight
]

UI_COLOR_DEFINITIONS = [
    (11, curses.COLOR_CYAN,   -1),
    (12, curses.COLOR_YELLOW, -1),
    (13, curses.COLOR_MAGENTA, -1),
    (14, curses.COLOR_WHITE,  curses.COLOR_BLUE),
    (15, curses.COLOR_GREEN,  -1),
    (16, curses.COLOR_YELLOW, -1), # Filler
    (17, curses.COLOR_RED,    -1)  # Used for DebugDot
]

# Combine them if you like, or keep them separate
ALL_COLOR_DEFINITIONS = MAP_COLOR_DEFINITIONS + UI_COLOR_DEFINITIONS

# A dictionary mapping human-friendly names -> pair index
COLOR_PAIR_NAMES = {
    "TREE_TOP": 1,
    "BRIDGE":   2,
    "ROCK":     3,
    "RIVER":    4,
    "GRASS":    5,
    "ASCII_ART":6,
    "TREE_HIDE_PLAYER":7,
    "PATH":     8,
    "WHITE_TEXT":9,
    "FLASH":    10,

    "UI_CYAN":  11,
    "UI_YELLOW":12,
    "UI_MAGENTA":13,
    "UI_WHITE_ON_BLUE":14,
    "UI_GREEN":15,
    "FILLER":   16,
    "DebugDot": 17,
}