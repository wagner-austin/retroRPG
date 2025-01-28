# FileName: scene_main.py
# version: 1.1 (added a Settings scene)
# Summary: High-level scene functions that combine animation, UI, and input loops (title screen, load screen).
# Tags: scene, animation, menu

import curses

from color_init import color_pairs
from art_main import MAIN_MENU_ART, CROCODILE
from ui_main import (
    draw_screen_frame,
    draw_title,
    draw_instructions
)
from animator_draw import draw_art


def scene_home_screen(stdscr):
    """
    Animates MAIN_MENU_ART left/right ±2 columns, draws menu instructions,
    and returns:
      1 (play),
      2 (quit),
      3 (settings) 
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
        draw_screen_frame(stdscr)

        draw_title(stdscr, "Welcome to Retro RPG!", row=1)

        menu_lines = [
            "~~~~~~~~~",
            "1) Play",
            #"3) Settings",
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
            if key in (ord('1'), ord('p'), ord('P'), curses.KEY_ENTER, 10, 13):
                return 1
            elif key in (ord('2'), ord('q'), ord('Q'), 27):
                return 2
            elif key in (ord('3'), ord('s'), ord('S')):
                return 3
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


def scene_load_screen(stdscr):
    """
    Shows animated CROCODILE art for the Load Map screen.
    This function no longer does map selection; it just animates
    until the user presses Enter/ESC/'q'/Backspace, then returns None.
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
        draw_screen_frame(stdscr)
        draw_title(stdscr, "Load Map", row=1)
        draw_art(stdscr, CROCODILE, start_row=3, start_col=2 + offset_x)

        instructions = [
            "↑/↓=select, ENTER=load, 'd'=del, 'q'=back"
            # No text update for backspace, per your request.
        ]
        draw_instructions(stdscr, instructions, from_bottom=3, color_name="UI_YELLOW")

        stdscr.noutrefresh()
        curses.doupdate()

        key = stdscr.getch()
        # Add backspace checks: curses.KEY_BACKSPACE or ASCII 127
        if key in (
            ord('q'), ord('Q'), 27,  # ESC
            curses.KEY_ENTER, 10, 13,  # Enter
            curses.KEY_BACKSPACE, 127  # Backspace
        ):
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


def scene_settings_screen(stdscr):
    """
    A placeholder "Settings" screen, demonstrating how you can
    create new screens for future expansions.
    Press 'q' or ESC to return to the main menu.
    """
    stdscr.nodelay(False)
    stdscr.keypad(True)
    curses.curs_set(0)

    while True:
        stdscr.erase()
        draw_screen_frame(stdscr)
        draw_title(stdscr, "Settings (Placeholder)", row=1)

        info_lines = [
            "Here is where you might configure volume, video settings, etc.",
            "Press 'q' or ESC to go back..."
        ]
        draw_instructions(stdscr, info_lines, from_bottom=2, color_name="UI_YELLOW")

        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord('q'), ord('Q'), 27):
            # Return to main menu
            return
        elif key == ord('v'):
            import debug
            debug.toggle_debug()