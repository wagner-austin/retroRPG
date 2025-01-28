# FileName: scene_main.py
# version: 1.2 (Uses highlight_selector for arrow-key selection on home screen)
# Summary: High-level scene functions (title screen, load screen, etc.)
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

# NEW: Instead of pulling from ui_main, we use highlight_selector
from highlight_selector import draw_selectable_line

def scene_home_screen(stdscr):
    """
    Animates MAIN_MENU_ART left/right ±2 columns, draws menu instructions,
    and allows user to select:
      1 (play),
      2 (quit),
      3 (settings)
    Either by arrow keys or by pressing '1', '2', or '3'.
    
    Return:
      1 => play
      2 => quit
      3 => settings
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

    # The lines shown near bottom (unchanged text):
    menu_lines = [
        "~~~~~~~~~",
        "1) Play",
        # "3) Settings", <-- omitted in text but user can press '3'
        "2) Quit",
        "~~~~~~~~~"
    ]
    # Only indices 1 and 2 are selectable lines
    selectable_indices = [1, 2]
    current_select_slot = 0  # 0 => "1) Play"; 1 => "2) Quit"

    while True:
        stdscr.erase()
        draw_screen_frame(stdscr)

        draw_title(stdscr, "Welcome to Retro RPG!", row=1)

        # Animate ASCII art
        draw_art(stdscr, MAIN_MENU_ART, start_row=3, start_col=2 + offset_x)

        # Draw the lines near the bottom, highlight whichever is selected
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

            draw_selectable_line(
                stdscr,
                row,
                line_text,
                is_selected=is_selected,
                color_name="UI_YELLOW",
                effect="SHIMMER",  # or "FLASH", "GLOW", "SHIMMER" etc.
                frame=frame_count
            )
            row += 1

        stdscr.noutrefresh()
        curses.doupdate()

        # Handle input
        key = stdscr.getch()
        if key != -1:
            if key in (curses.KEY_UP, ord('w'), ord('W')):
                current_select_slot = max(0, current_select_slot - 1)
            elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
                if current_select_slot < len(selectable_indices) - 1:
                    current_select_slot += 1
            elif key in (curses.KEY_ENTER, 10, 13):
                # If current_select_slot == 0 => "1) Play"
                if current_select_slot == 0:
                    return 1
                else:
                    return 2

            # Numeric shortcuts remain the same:
            elif key == ord('1'):
                return 1
            elif key == ord('2'):
                return 2
            elif key == ord('3') or key in (ord('s'), ord('S')):
                return 3
            elif key in (ord('q'), ord('Q'), 27):
                return 2
            elif key == ord('v'):
                import debug
                debug.toggle_debug()

        # Animate the left/right shift
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
        ]
        draw_instructions(stdscr, instructions, from_bottom=3, color_name="UI_YELLOW")

        stdscr.noutrefresh()
        curses.doupdate()

        key = stdscr.getch()
        if key in (
            ord('q'), ord('Q'), 27,
            curses.KEY_ENTER, 10, 13,
            curses.KEY_BACKSPACE, 127
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
            return
        elif key == ord('v'):
            import debug
            debug.toggle_debug()