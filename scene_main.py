# FileName: scene_main.py
# version: 1.2 (Arrow-key selector added to home screen, preserving number selection)
# Summary: High-level scene functions that combine animation, UI, and input loops (title screen, load screen).
# Tags: scene, animation, menu

import curses

from color_init import color_pairs
from art_main import MAIN_MENU_ART, CROCODILE
from ui_main import (
    draw_screen_frame,
    draw_title,
    draw_instructions,
    draw_selectable_line,        # to highlight the menu lines
    get_selector_effect_attrs
)
from animator_draw import draw_art


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

    # The lines we show near bottom; do not change text:
    # (We will highlight lines [1, 2] in this array: "1) Play" => index 1, "2) Quit" => index 2)
    menu_lines = [
        "~~~~~~~~~",
        "1) Play",
        # "3) Settings",   <-- commented out in text, but we still accept '3' input
        "2) Quit",
        "~~~~~~~~~"
    ]
    # Indices that are actually selectable: we won't highlight the "~~~~~~~~~"
    selectable_indices = [1, 2]  # only these lines are "selectable"
    current_select_slot = 0  # 0 => line #1 ("1) Play"), 1 => line #2 ("2) Quit")

    while True:
        stdscr.erase()
        draw_screen_frame(stdscr)

        draw_title(stdscr, "Welcome to Retro RPG!", row=1)

        # Animate ASCII art
        draw_art(stdscr, MAIN_MENU_ART, start_row=3, start_col=2 + offset_x)

        # Draw the same lines we always do near bottom, 
        # but highlight whichever is currently selected.
        # We do not add or remove text; we only invert or blink the selected line.
        h, w = stdscr.getmaxyx()
        from_bottom = 2
        start_row = h - from_bottom - len(menu_lines)
        if start_row < 1:
            start_row = 1

        row = start_row
        for i, line_text in enumerate(menu_lines):
            is_selected = False
            # Check if this line is one of the selectable lines 
            # and if it matches the current selected "slot"
            if i in selectable_indices:
                # find the "index" within selectable_indices
                sel_index = selectable_indices.index(i)
                if sel_index == current_select_slot:
                    is_selected = True

            draw_selectable_line(
                stdscr,
                row,
                line_text,
                is_selected=is_selected,
                color_name="UI_YELLOW",
                # You can switch effect to "REVERSE", "NONE", "REVERSE_BLINK", etc.
                effect="REVERSE_BLINK"
            )
            row += 1

        stdscr.noutrefresh()
        curses.doupdate()

        # Handle input
        key = stdscr.getch()
        if key != -1:
            # If arrow up => move selection up
            if key in (curses.KEY_UP, ord('w'), ord('W')):
                current_select_slot -= 1
                if current_select_slot < 0:
                    current_select_slot = 0
            # If arrow down => move selection down
            elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
                if current_select_slot < len(selectable_indices) - 1:
                    current_select_slot += 1

            # If user presses Enter => confirm the selected item
            elif key in (curses.KEY_ENTER, 10, 13):
                # If current_select_slot == 0 => line #1 => "1) Play"
                if current_select_slot == 0:
                    return 1
                else:
                    return 2

            # If user presses numeric keys, follow existing logic (no text changed):
            elif key == ord('1'):
                return 1
            elif key == ord('2'):
                return 2
            elif key == ord('3') or key in (ord('s'), ord('S')):
                return 3
            elif key in (ord('q'), ord('Q'), 27):
                # treat 'q' or ESC as "2) Quit":
                return 2
            elif key == ord('v'):
                import debug
                debug.toggle_debug()

        # Animate the left/right shift for ASCII art
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
            # Return to main menu
            return
        elif key == ord('v'):
            import debug
            debug.toggle_debug()