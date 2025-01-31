# FileName: curses_scene_manager.py
#
# version: 2.1
#
# Summary: Contains the high-level MenuFlowManager class that organizes
#          the main menu screens (HOME, SETTINGS, PLAY), calling each scene.
#
# Tags: scene, menu, manager

import curses
import debug

# The home screen is in curses_scene_home.py
from .curses_scene_home import scene_home_screen
# The settings screen is now in curses_scene_settings.py
from .curses_scene_settings import run_settings_scene
# The load-map UI is in curses_scene_load.py
from .curses_scene_load import load_map_ui
# The game-play runner:
from play_runner import parse_and_run_play


class MenuFlowManager:
    """
    A simple controller that organizes the main menu screens (HOME, SETTINGS, PLAY)
    and transitions between them. The PLAY flow loads or generates a map, then calls
    parse_and_run_play(...) to run the game.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_state = "HOME"
        self.running = True

    def run(self):
        while self.running:
            if self.current_state == "HOME":
                # scene_home_screen returns:
                #   1 => "Play"
                #   2 => "Quit"
                #   3 => "Settings"
                choice = scene_home_screen(self.stdscr)
                if choice == 1:
                    self.current_state = "PLAY"
                elif choice == 2:
                    self.current_state = "QUIT"
                else:
                    self.current_state = "SETTINGS"

            elif self.current_state == "PLAY":
                # Let the user pick or generate a map
                while True:
                    selection = load_map_ui(self.stdscr)
                    if not selection:
                        # user canceled => back to main menu
                        self.current_state = "HOME"
                        break

                    # If load_map_ui returns a tuple
                    if isinstance(selection, tuple):
                        action_type, actual_map = selection
                        if action_type == "EDIT_GENERATE":
                            parse_and_run_play(self.stdscr, actual_map, is_generated=True)
                        elif action_type == "EDIT":
                            parse_and_run_play(self.stdscr, actual_map, is_generated=False)

                    elif isinstance(selection, dict):
                        # user generated a new map => is_generated = True
                        parse_and_run_play(self.stdscr, selection, is_generated=True)
                    else:
                        # user picked an existing map filename => is_generated = False
                        parse_and_run_play(self.stdscr, selection, is_generated=False)

            elif self.current_state == "SETTINGS":
                run_settings_scene(self.stdscr)
                self.current_state = "HOME"

            elif self.current_state == "QUIT":
                self.running = False