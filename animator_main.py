# FileName: animator_main.py
# version: 2.2
# Summary: Manages low-level animation updates (e.g. subtle ASCII art shifts).
#          High-level "scene" logic has been moved to scene_main.py.
# Tags: animation, transitions

import curses
import debug
from animator_draw import draw_art

def animate_art_subtle(
    stdscr,
    art_lines,
    title_text=None,
    max_shift=2,
    frame_delay_ms=50,
    shift_delay_frames=20
):
    """
    Slowly shifts ASCII art left/right by ±max_shift columns,
    pausing shift_delay_frames between shifts.
    Press 'q'/'Q' or ESC to exit.
    Optional: 'title_text' can be displayed at row=1, col=2 (if desired).
    """
    stdscr.nodelay(True)
    curses.curs_set(0)

    offset_x = -2
    direction = -1
    frame_count = 0

    while True:
        stdscr.erase()

        # If given, display some title text
        if title_text:
            try:
                stdscr.addstr(1, 2, title_text, curses.A_BOLD)
            except curses.error:
                pass

        # Render art offset by offset_x
        draw_art(stdscr, art_lines, start_row=3, start_col=2 + offset_x)

        # Double-buffer
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

        curses.napms(frame_delay_ms)