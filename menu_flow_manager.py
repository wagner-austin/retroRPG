# FileName: menu_flow_manager.py
# version: 1.0
# Summary: A controller that manages high-level menu flow (title, play, settings, etc.)
# Tags: menu, flow, controller

import curses

# We import the scene functions and play_main so we can call them:
from scene_main import scene_home_screen, scene_settings_screen
from play_main import play_main

class MenuFlowManager:
    """
    A simple UI flow controller that organizes the main menu screens (home, settings, etc.)
    and transitions to play mode or quits. Future expansions (multiplayer, level select, etc.)
    can be plugged in here by adding new states and new scene calls.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_state = "HOME"
        self.running = True

    def run(self):
        """
        Main loop for the menu flow. Each screen function returns
        a choice that we interpret to move to the next state or exit.
        """
        while self.running:
            if self.current_state == "HOME":
                choice = scene_home_screen(self.stdscr)
                if choice == 1:
                    # user selected "Play"
                    self.current_state = "PLAY"
                elif choice == 2:
                    # user selected "Quit"
                    self.current_state = "QUIT"
                elif choice == 3:
                    # user selected "Settings"
                    self.current_state = "SETTINGS"
                else:
                    # Just in case we get something else, quit by default
                    self.current_state = "QUIT"

            elif self.current_state == "PLAY":
                # We run the existing play mode, then return to HOME afterward
                play_main(self.stdscr)
                self.current_state = "HOME"

            elif self.current_state == "SETTINGS":
                # Run the new (placeholder) settings screen,
                # then return to HOME after it's done
                scene_settings_screen(self.stdscr)
                self.current_state = "HOME"

            elif self.current_state == "QUIT":
                self.running = False

        # End of run() => Flow manager is done.
