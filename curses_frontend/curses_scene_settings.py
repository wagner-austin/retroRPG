# FileName: curses_scene_settings.py
#
# version: 1.0
#
# Summary: Defines the "Settings" scene, with its own while-True loop for user input.
#
# Tags: scene, settings

import curses
import debug
from .curses_common import draw_screen_frame, draw_title, draw_instructions

def run_settings_scene(stdscr):
    """
    A placeholder 'Settings' screen. Press 'q' or ESC to return to the main menu.
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
        draw_instructions(stdscr, info_lines, from_bottom=2)

        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord('q'), ord('Q'), 27):
            # 'q' or ESC => exit settings
            return
        elif key == ord('v'):
            debug.toggle_debug()
