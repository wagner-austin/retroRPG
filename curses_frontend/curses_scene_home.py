# FileName: curses_scene_home.py
#
# version: 1.1
#
# Summary: Defines the 'scene_home_screen' function for the main / title screen.
#          Now with no animation loop; we simply draw a static banner (if desired).
#
# Tags: scene, home, menu

import curses
import debug

from .curses_common import draw_screen_frame, draw_title, _draw_art
from .curses_selector_highlight import draw_global_selector_line
from .where_curses_themes_lives import CURRENT_THEME


def home_scene_ui(stdscr):
    """
    The main 'home screen' with a static ASCII banner (optional)
    and a simple menu for Play/Quit/Settings. Returns:
      1 => Play
      2 => Quit
      3 => Settings
    """
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.curs_set(0)

    # Grab the ASCII art for the main menu from the current theme
    main_menu_lines = CURRENT_THEME["main_menu_art"]

    menu_lines = [
        "~~~~~~~~~",
        "1) Play",
        "2) Quit",
        "3) Settings",
        "~~~~~~~~~"
    ]
    # We'll consider lines #1 => "1) Play", #2 => "2) Quit", #3 => "3) Settings"
    selectable_indices = [1, 2, 3]

    current_select_slot = 0
    frame_count = 0

    while True:
        stdscr.erase()
        draw_screen_frame(stdscr)
        draw_title(stdscr, "Welcome to Retro RPG!", row=1)

        # If you want to show a *static* ASCII banner, do it here:
        _draw_art(stdscr, main_menu_lines, start_row=3, start_col=2)

        # Draw menu near the bottom
        h, w = stdscr.getmaxyx()
        from_bottom = 2
        start_row = h - from_bottom - len(menu_lines)
        if start_row < 1:
            start_row = 1

        row = start_row
        for i, line_text in enumerate(menu_lines):
            is_selected = False
            if i in selectable_indices:
                sel_index = selectable_indices.index(i)
                if sel_index == current_select_slot:
                    is_selected = True
            draw_global_selector_line(
                stdscr,
                row,
                line_text,
                is_selected=is_selected,
                frame=frame_count
            )
            row += 1

        stdscr.noutrefresh()
        curses.doupdate()

        key = stdscr.getch()
        if key != -1:
            # Simple up/down to cycle among 3 menu items
            if key in (curses.KEY_UP, ord('w'), ord('W')):
                current_select_slot = max(0, current_select_slot - 1)
            elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
                if current_select_slot < len(selectable_indices) - 1:
                    current_select_slot += 1
            elif key in (curses.KEY_ENTER, 10, 13, 32):
                # user pressed Enter on the current slot
                if current_select_slot == 0:
                    return 1  # Play
                elif current_select_slot == 1:
                    return 2  # Quit
                else:
                    return 3  # Settings
            elif key == ord('1'):
                return 1  # Play
            elif key == ord('2'):
                return 2  # Quit
            elif key == ord('3'):
                return 3  # Settings
            elif key in (ord('q'), ord('Q'), 27):
                return 2  # user pressed Esc => Quit
            elif key in (ord('v'), ord ('V')):
                debug.toggle_debug()

        frame_count += 1