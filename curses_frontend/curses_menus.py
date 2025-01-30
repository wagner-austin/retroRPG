# FileName: curses_menus.py
#
# version: 2.0
#
# Summary: High-level scene/menu functions (title screen, load screen, settings),
#          plus the consolidated MenuFlowManager for controlling menu flow.
#
# Tags: scene, animation, menu

import curses
import debug

from .curses_common import draw_screen_frame, draw_title, draw_instructions
from .curses_animations import _draw_art
from .curses_art_skins import MAIN_MENU_ART, CROCODILE, CURRENT_SKIN
from .curses_highlight import draw_global_selector_line
from .curses_renderer import CursesGameRenderer  # For example usage if we want
from play_main import play_main

def scene_home_screen(stdscr):
    """
    Example 'home screen' that animates MAIN_MENU_ART left/right ±2 columns,
    then shows menu instructions. Returns:
      1 => Play
      2 => Quit
      3 => Settings
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

    main_menu_lines = MAIN_MENU_ART
    menu_lines = [
        "~~~~~~~~~",
        "1) Play",
        "2) Quit",
        #"3) Settings",
        "~~~~~~~~~"
    ]
    # We'll consider lines #1 => "1) Play", #2 => "2) Quit", #3 => "3) Settings"
    selectable_indices = [1, 2, 3]
    current_select_slot = 0

    while True:
        stdscr.erase()
        draw_screen_frame(stdscr)

        draw_title(stdscr, "Welcome to Retro RPG!", row=1)
        _draw_art(stdscr, main_menu_lines, start_row=3, start_col=2 + offset_x)

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
            if key in (curses.KEY_UP, ord('w'), ord('W')):
                current_select_slot = max(0, current_select_slot - 1)
            elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
                if current_select_slot < len(selectable_indices) - 1:
                    current_select_slot += 1
            elif key in (curses.KEY_ENTER, 10, 13):
                # user pressed enter on the current slot
                if current_select_slot == 0:
                    return 1  # Play
                elif current_select_slot == 1:
                    return 2  # Quit
                else:
                    return 3  # Settings
            elif key == ord('1'):
                return 1
            elif key == ord('2'):
                return 2
            elif key == ord('3'):
                return 3
            elif key in (ord('q'), ord('Q'), 27):
                return 2
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

def scene_settings_screen(stdscr):
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
            return
        elif key == ord('v'):
            debug.toggle_debug()

# ------------------------------------------------------------------------
# LAYERED SCENE EXAMPLE (for advanced usage)
# ------------------------------------------------------------------------
def example_layered_scene(curses_renderer):
    """
    If you wanted to define layering for a menu scene, you'd do something like:

    scene_layers = [
      {"name": "background_layer", "visible": True,  "z": 0},
      {"name": "art_layer",        "visible": True,  "z": 1},
      {"name": "menu_overlay",     "visible": True,  "z": 2}
    ]
    curses_renderer.render_scene(model=None, scene_layers=scene_layers)

    In this demonstration, we do not have a "model," so we might pass None or a dummy.
    You would implement the code for each layer's rendering logic inside
    CursesGameRenderer.render_scene(...).
    """
    pass

# ------------------------------------------------------------------------
# CONSOLIDATED MENU FLOW MANAGER
# ------------------------------------------------------------------------
class MenuFlowManager:
    """
    A simple controller that organizes the main menu screens (home, settings, etc.)
    and transitions to Play mode or quits. This replaced the old 'menu_flow_manager.py'.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_state = "HOME"
        self.running = True

    def run(self):
        while self.running:
            if self.current_state == "HOME":
                choice = scene_home_screen(self.stdscr)
                if choice == 1:
                    # user selected Play
                    self.current_state = "PLAY"
                elif choice == 2:
                    # user selected Quit
                    self.current_state = "QUIT"
                else:
                    # Settings
                    self.current_state = "SETTINGS"

            elif self.current_state == "PLAY":
                # Run the existing play mode, then return to HOME afterward
                play_main(self.stdscr)
                self.current_state = "HOME"

            elif self.current_state == "SETTINGS":
                scene_settings_screen(self.stdscr)
                self.current_state = "HOME"

            elif self.current_state == "QUIT":
                self.running = False

        # End of run => done