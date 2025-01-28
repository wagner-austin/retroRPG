# FileName: ui_main.py
# version: 2.1 (Removed duplicate draw_border, draw_art, animate_home_screen)
# Summary: Provides functions and helpers for drawing frames, labels, and other UI elements on screen.
# Tags: ui, rendering, curses

import curses
from color_init import color_pairs

# Import the actual "draw_border" and "draw_art" from animator_draw:
from animator_draw import draw_border, draw_art

# Use these color constants for easy reference in this module
BORDER_COLOR_NAME     = "UI_CYAN"
TITLE_COLOR_NAME      = "UI_WHITE_ON_BLUE"
TEXT_COLOR_NAME       = "WHITE_TEXT"
HIGHLIGHT_COLOR_NAME  = "UI_YELLOW"
ART_COLOR_NAME        = "ASCII_ART"

def draw_title(stdscr, text, row=1, color_name=TITLE_COLOR_NAME):
    """
    Draws a title line at a given row with the specified color_name.
    """
    max_h, max_w = stdscr.getmaxyx()
    if row < 0 or row >= max_h:
        return
    col = 2
    title_color = curses.color_pair(color_pairs[color_name]) | curses.A_BOLD
    try:
        stdscr.addstr(row, col, text[:max_w-col-1], title_color)
    except curses.error:
        pass

def draw_instructions(stdscr, lines, from_bottom=2, color_name=HIGHLIGHT_COLOR_NAME):
    """
    Draws instruction lines near the bottom of the screen using the specified color_name.
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
        truncated = line[:w-4]
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
            # Place it near the top-right, 
            # row=0, col ~ max_w - len(label) - 2
            col = max_w - len(label) - 2
            debug_color = curses.color_pair(color_pairs["WHITE_TEXT"])
            stdscr.addstr(0, col, label, debug_color)
    except:
        pass