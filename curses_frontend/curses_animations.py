# FileName: curses_animations.py
#
# version: 2.0
#
# Summary: Houses drawing routines for sprite/scene animations (ASCII art, borders),
#          plus the subtle ASCII art shifting from the old animator_main.py.
#
# Tags: animation, drawing, curses

import time
import curses
import debug
from .curses_utils import safe_addstr, safe_addch, get_color_attr
from .curses_common import draw_screen_frame
from .curses_art_skins import DECORATION

def animate_art_subtle(stdscr, art_lines, title_text=None, max_shift=2, frame_delay_ms=50, shift_delay_frames=20):
    """
    Slowly shifts ASCII art left/right by ±max_shift columns, pausing shift_delay_frames frames
    between each shift. Press 'q'/'Q' or ESC to exit. Press 'v' to toggle debug.
    
    :param stdscr: The curses screen
    :param art_lines: list of strings for the ASCII art
    :param title_text: optional string displayed at row=1, col=2
    :param max_shift: maximum shift in columns (default 2)
    :param frame_delay_ms: time to sleep each frame, in milliseconds (default 50)
    :param shift_delay_frames: how many frames to wait before reversing shift direction
    """
    stdscr.nodelay(True)
    curses.curs_set(0)

    offset_x = -2
    direction = -1
    frame_count = 0

    while True:
        stdscr.erase()
        draw_screen_frame(stdscr)

        # If given, display some title text
        if title_text:
            try:
                safe_addstr(stdscr, 1, 2, title_text, get_color_attr("WHITE_TEXT"), clip_borders=False)
            except curses.error:
                pass

        # Render art offset by offset_x
        _draw_art(stdscr, art_lines, start_row=3, start_col=2 + offset_x)

        stdscr.noutrefresh()
        curses.doupdate()

        key = stdscr.getch()
        if key in (ord('q'), ord('Q'), 27):
            break
        elif key == ord('v'):
            debug.toggle_debug()

        frame_count += 1
        if frame_count % shift_delay_frames == 0:
            offset_x += direction
            if offset_x >= max_shift:
                offset_x = max_shift
                direction = -1
            elif offset_x <= -max_shift:
                offset_x = -max_shift
                direction = 1

        # Use time.sleep for frame delay (instead of curses.napms).
        time.sleep(frame_delay_ms / 1000.0)


def _draw_art(stdscr, art_lines, start_row=1, start_col=2, color_name="ASCII_ART"):
    """
    Renders 'art_lines' at (start_row, start_col), using a specified color_name.
    """
    attr = get_color_attr(color_name)
    max_h, max_w = stdscr.getmaxyx()
    row = start_row
    for line in art_lines:
        if row >= max_h - 1:
            break
        safe_addstr(stdscr, row, start_col, line, attr, clip_borders=True)
        row += 1


#def draw_border_old(stdscr, color_name="UI_CYAN"):
#    """
#    DEPRECATED: We keep this for reference, but prefer using 'draw_screen_frame' from curses_common.
#    """
#    draw_screen_frame(stdscr, color_name)