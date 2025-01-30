# FileName: animator_draw.py
# version: 1.4
# Summary: Houses drawing routines for sprite/scene animations, used by animator logic.
# Tags: animation, drawing

import curses
from curses_utils import safe_addch, safe_addstr, get_color_attr
from color_init import color_pairs

def draw_border(stdscr: curses.window, color_name: str = "UI_CYAN") -> None:
    """
    Draws a rectangular border around the entire screen using the given color_name.
    Using clip_borders=False so we can place chars at col=0 and col=w-1.
    """
    h, w = stdscr.getmaxyx()
    if h < 3 or w < 3:
        return
    border_attr = get_color_attr(color_name)

    # top line
    for x in range(w):
        safe_addch(stdscr, 0, x, curses.ACS_HLINE, border_attr, clip_borders=False)
    safe_addch(stdscr, 0, 0, curses.ACS_ULCORNER, border_attr, clip_borders=False)
    safe_addch(stdscr, 0, w-1, curses.ACS_URCORNER, border_attr, clip_borders=False)

    # bottom line
    for x in range(w):
        safe_addch(stdscr, h-1, x, curses.ACS_HLINE, border_attr, clip_borders=False)
    safe_addch(stdscr, h-1, 0, curses.ACS_LLCORNER, border_attr, clip_borders=False)
    safe_addch(stdscr, h-1, w-1, curses.ACS_LRCORNER, border_attr, clip_borders=False)

    # left/right vertical lines
    for y in range(1, h-1):
        safe_addch(stdscr, y, 0, curses.ACS_VLINE, border_attr, clip_borders=False)
        safe_addch(stdscr, y, w-1, curses.ACS_VLINE, border_attr, clip_borders=False)


def draw_art(stdscr: curses.window,
             art_lines: list[str],
             start_row: int = 1,
             start_col: int = 2,
             color_name: str = "ASCII_ART") -> None:
    """
    Renders 'art_lines' at (start_row, start_col), truncating if needed.
    By default, clip_borders=True => no overflow into col=0/w-1.
    """
    attr = get_color_attr(color_name)
    max_h, max_w = stdscr.getmaxyx()
    row = start_row
    for line in art_lines:
        if row >= max_h - 1:
            break
        safe_addstr(stdscr, row, start_col, line, attr, clip_borders=True)
        row += 1