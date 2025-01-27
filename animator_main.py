# FileName: animator_main.py
# version: 2.0 (UPDATED)
# Focuses on subtle ASCII animation loops (animate_art_subtle, animate_home_screen, etc.)

import curses
from color_init import color_pairs
from art_main import MAIN_MENU_ART, CROCODILE
# CHANGED: import draw_screen_frame instead of draw_border
from ui_main import draw_title, draw_instructions, draw_screen_frame

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
    Slowly shift ASCII art left/right by ±max_shift columns,
    pausing shift_delay_frames between shifts.
    Press 'q'/'Q' or ESC to exit.
    """

    stdscr.nodelay(True)
    curses.curs_set(0)

    offset_x = -2
    direction = -1
    frame_count = 0

    while True:
        stdscr.erase()
        draw_screen_frame(stdscr)  # CHANGED

        if title_text:
            color = curses.color_pair(color_pairs["WHITE_TEXT"]) | curses.A_BOLD
            try:
                stdscr.attron(color)
                stdscr.addstr(1, 2, title_text)
                stdscr.attroff(color)
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
            import debug
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

def animate_home_screen(stdscr):
    """
    Animates MAIN_MENU_ART left/right ±2 columns, draws menu instructions, 
    and returns 1 (play) or 2 (quit).
    """
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.curs_set(0)

    max_shift = 2
    frame_delay_ms = 50
    shift_delay_frames = 20

    offset_x = 0
    direction = -1
    frame_count = 0

    while True:
        stdscr.erase()
        draw_screen_frame(stdscr)  # CHANGED

        draw_title(stdscr, "Welcome to Retro RPG!", row=1)

        menu_lines = [
            "~~~~~~~~~",
            "1) Play",
            "2) Quit",
            "~~~~~~~~~"
        ]
        draw_instructions(stdscr, menu_lines, from_bottom=2, color_name="UI_YELLOW")

        # Animate ASCII art
        draw_art(stdscr, MAIN_MENU_ART, start_row=3, start_col=2 + offset_x)

        stdscr.noutrefresh()
        curses.doupdate()

        key = stdscr.getch()
        if key != -1:
            if key in (ord('1'), ord('p'), ord('P')):
                return 1
            elif key in (ord('2'), ord('q'), ord('Q'), 27):
                return 2
            elif key == ord('v'):
                import debug
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

def animate_load_screen(stdscr):
    """
    Shows animated CROCODILE art for the Load Map screen. 
    This function no longer does any map selection itself—
    it just animates until the user presses Enter/ESC/'q',
    then returns None. The actual load logic happens in map_io_ui.py.
    """
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.curs_set(0)

    max_shift = 2
    frame_delay_ms = 50
    shift_delay_frames = 20

    offset_x = 0
    direction = -1
    frame_count = 0

    while True:
        stdscr.erase()
        draw_screen_frame(stdscr)  # CHANGED

        draw_title(stdscr, "Load Map", row=1)
        draw_art(stdscr, CROCODILE, start_row=3, start_col=2 + offset_x)

        instructions = [
            "↑/↓=select, ENTER=load, 'd'=del, 'q'=back"
        ]
        draw_instructions(stdscr, instructions, from_bottom=3, color_name="UI_YELLOW")

        stdscr.noutrefresh()
        curses.doupdate()

        key = stdscr.getch()
        if key in (ord('q'), ord('Q'), 27, curses.KEY_ENTER, 10, 13):
            return None
        elif key == ord('v'):
            import debug
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