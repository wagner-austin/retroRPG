# FileName: curses_animations.py
#
# version: 2.2
#
# Summary: Houses drawing routines for sprite/scene animations (ASCII art, borders),
#          with no permanent loops or direct user input logic. 
#
# Tags: animation, drawing, curses

import curses
import debug
from .curses_utils import safe_addstr, safe_addch, get_color_attr
from .curses_common import draw_screen_frame
from .curses_art_skins import DECORATION

def draw_subtle_art_frame(stdscr, art_lines, offset_x, start_row=3, start_col=2, color_name="ASCII_ART"):
    """
    Draw one 'frame' of the ASCII art shifted horizontally by offset_x.
    Currently unused in the home screen, but kept here in case you 
    want to re-enable animations in the future.
    """
    _draw_art(stdscr, art_lines, start_row=start_row, start_col=start_col + offset_x, color_name=color_name)

def _draw_art(stdscr, art_lines, start_row=1, start_col=2, color_name="ASCII_ART"):
    """
    Renders 'art_lines' at (start_row, start_col), using a specified color_name.
    Safe for static or single-frame usage.
    """
    attr = get_color_attr(color_name)
    max_h, max_w = stdscr.getmaxyx()
    row = start_row
    for line in art_lines:
        if row >= max_h - 1:
            break
        safe_addstr(stdscr, row, start_col, line, attr, clip_borders=True)
        row += 1