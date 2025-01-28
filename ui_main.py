# FileName: ui_main.py
# version: 2.5
# Summary: Provides functions and helpers for drawing frames, labels, etc.
#          Now includes a UI_FONT_CONFIG to control normal text “font” color, size, etc.
# Tags: ui, rendering, curses

import curses
from color_init import color_pairs
from animator_draw import draw_border, draw_art

# We rename this so it's clear it's for instructions specifically, 
# NOT the same highlight used by highlight_selector:
INSTRUCTION_COLOR_NAME = "UI_MAGENTA"

# Pre-existing color constants for certain UI elements:
BORDER_COLOR_NAME     = "UI_CYAN"
TITLE_COLOR_NAME      = "UI_WHITE_ON_BLUE"
TEXT_COLOR_NAME       = "YELLOW_TEXT"
ART_COLOR_NAME        = "ASCII_ART"

# A new config dict for "font" style in normal UI text
# (size, type are conceptual placeholders, as curses doesn't truly do that).
UI_FONT_CONFIG = {
    "font_color_name": TEXT_COLOR_NAME,   # normal text color
    "font_size": None,                    # can't truly scale in curses, but you can store it
    "font_type": None,                    # likewise, a placeholder for custom usage
}


def set_ui_font_config(**kwargs):
    """
    Allows the game to update normal UI font properties,
    e.g. set_ui_font_config(font_color_name="WHITE_TEXT", font_size=12, font_type="Courier")
    """
    for key, val in kwargs.items():
        if key in UI_FONT_CONFIG:
            UI_FONT_CONFIG[key] = val


def draw_title(stdscr, text, row=1, color_name=TITLE_COLOR_NAME):
    """
    Draws a title line at a given row with the specified color_name.
    Falls back to UI_FONT_CONFIG if you prefer to override usage.
    """
    max_h, max_w = stdscr.getmaxyx()
    if row < 0 or row >= max_h:
        return

    col = 2
    # If you wanted to use the custom UI_FONT_CONFIG color instead, you could do:
    # color_name = UI_FONT_CONFIG["font_color_name"]
    # But for now, this function specifically uses the "title color" by default:
    title_color = curses.color_pair(color_pairs[color_name]) | curses.A_BOLD

    truncated = text[:max_w - col - 1]
    try:
        stdscr.addstr(row, col, truncated, title_color)
    except curses.error:
        pass


def draw_instructions(stdscr, lines, from_bottom=2, color_name=INSTRUCTION_COLOR_NAME):
    """
    Draws instruction lines near the bottom of the screen using the specified color_name.
    By default, we pass INSTRUCTION_COLOR_NAME (UI_MAGENTA).
    """
    h, w = stdscr.getmaxyx()
    color = curses.color_pair(color_pairs[color_name])
    start_row = h - from_bottom - len(lines)
    if start_row < 1:
        start_row = 1

    row = start_row
    for line in lines:
        if row >= h - 1:
            break
        truncated = line[:w - 4]
        try:
            stdscr.addstr(row, 2, truncated, color)
        except curses.error:
            pass
        row += 1


def draw_screen_frame(stdscr, color_name=BORDER_COLOR_NAME):
    """
    Draws the border, then (if debug is enabled) draws "Debug mode: On" 
    in the top-right of the screen.
    """
    # 1) Draw the existing border
    draw_border(stdscr, color_name)

    # 2) If debug is on, display "Debug mode: On" at top-right
    try:
        import debug
        if debug.DEBUG_CONFIG["enabled"]:
            max_h, max_w = stdscr.getmaxyx()
            label = "Debug mode: On"
            col = max_w - len(label) - 2
            debug_color = curses.color_pair(color_pairs["WHITE_TEXT"])
            stdscr.addstr(0, col, label, debug_color)
    except:
        pass