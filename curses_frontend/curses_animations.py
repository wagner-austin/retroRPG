# FileName: curses_animations.py
#
# version: 2.2
#
# Summary: Houses drawing routines for sprite/scene animations (ASCII art, borders), with no permanent loops or direct user input logic.
#
# Tags: animation, drawing, curses

import curses
import debug
from .curses_utils import safe_addstr, safe_addch, get_color_attr
from .curses_common import draw_screen_frame, _draw_art
from .where_curses_themes_lives import CURRENT_THEME  # Newly added for default color usage


def draw_subtle_art_frame(stdscr, art_lines, offset_x, start_row=3, start_col=2, color_name=None):
    """
    Draw one 'frame' of the ASCII art shifted horizontally by offset_x.
    If color_name is None, we use CURRENT_THEME's 'ascii_art_color'.
    """
    if color_name is None:
        color_name = CURRENT_THEME["ascii_art_color"]
    _draw_art(stdscr, art_lines, start_row=start_row, start_col=start_col + offset_x, color_name=color_name)
