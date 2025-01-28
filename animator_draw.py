# FileName: animator_draw.py
# version: 1.2
# Summary: Houses the drawing routines for sprite or scene animations, used by the animator logic.
# Tags: animation, drawing

import curses

# Previously: from colors import color_pairs
# Then we changed: from color_init import color_pairs
# Now do an absolute import from topdownrpg_v3:
from color_init import color_pairs

def draw_border(stdscr, color_name="UI_CYAN"):
    """
    Draws a rectangular border around the entire screen using the given color_name.
    """
    h, w = stdscr.getmaxyx()
    if h < 3 or w < 3:
        return
    border_color = curses.color_pair(color_pairs[color_name])
    try:
        stdscr.hline(0, 0, curses.ACS_HLINE, w, border_color)
        stdscr.addch(0, 0, curses.ACS_ULCORNER, border_color)
        stdscr.addch(0, w-1, curses.ACS_URCORNER, border_color)
        stdscr.hline(h-1, 0, curses.ACS_HLINE, w, border_color)
        stdscr.addch(h-1, 0, curses.ACS_LLCORNER, border_color)
        stdscr.addch(h-1, w-1, curses.ACS_LRCORNER, border_color)
        for row in range(1, h-1):
            stdscr.addch(row, 0, curses.ACS_VLINE, border_color)
            stdscr.addch(row, w-1, curses.ACS_VLINE, border_color)
    except curses.error:
        pass

def draw_art(stdscr, art_lines, start_row=1, start_col=2, color_name="ASCII_ART"):
    """
    Renders 'art_lines' at (start_row, start_col), truncating if needed.
    """
    art_color = curses.color_pair(color_pairs[color_name])
    max_h, max_w = stdscr.getmaxyx()
    row = start_row
    for line in art_lines:
        if row >= max_h - 1:
            break
        available_width = max_w - start_col - 1
        if available_width < 1:
            continue
        truncated = line[:available_width]
        try:
            stdscr.addstr(row, start_col, truncated, art_color)
        except curses.error:
            pass
        row += 1