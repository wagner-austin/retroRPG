# FileName: curses_scene_manager.py
# version: 3.7
#
# Summary: High-level MenuFlowManager for main menu screens (HOME, SETTINGS, GAME).
#          Defers map-saving logic to curses_scene_save.
#
# Tags: scene, menu, manager

import os
import json
import curses  # needed for user input

from .curses_scene_home import home_scene_ui
from .curses_scene_settings import settings_scene_ui
from .curses_scene_load import load_scene_ui
from .curses_scene_game import game_scene_ui
from .curses_color_init import init_colors
#from .curses_controls_ui import prompt_yes_no

# We now import the dedicated save logic from curses_scene_save
from .curses_scene_save import handle_post_game_scene_save

from player_char_io import save_player
from map_model_builder import build_model_common

#from play_runner import build_model_for_play


class MenuFlowManager:
    """
    Manages the main menu screens (HOME, SETTINGS, GAME).
    After the user leaves the game scene, we ensure that:
     - The player's data is always saved to player.json.
     - If it’s a new or existing map, we handle saving via the dedicated
       handle_post_game_scene_save() from curses_scene_save.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        init_colors()

        self.current_state = "HOME"
        self.running = True

    def run(self):
        while self.running:
            if self.current_state == "HOME":
                choice = home_scene_ui(self.stdscr)
                if choice == 1:  # Play
                    self.current_state = "PLAY"
                elif choice == 2:  # Quit
                    self.current_state = "QUIT"
                else:
                    self.current_state = "SETTINGS"

            elif self.current_state == "PLAY":
                while True:
                    selection = load_scene_ui(self.stdscr)
                    if not selection:
                        self.current_state = "HOME"
                        break

                    # 1) "GENERATE" => brand-new map
                    if selection == "GENERATE":
                        model, context = build_model_common({}, is_generated=True, mode_name="play")
                        if not model:
                            self.current_state = "HOME"
                            break

                        game_scene_ui(self.stdscr, model, context)
                        save_player(model.player)
                        handle_post_game_scene_save(self.stdscr, model)
                        continue

                    # 2) A dictionary => newly generated procedural data
                    if isinstance(selection, dict):
                        model, context = build_model_common (selection, is_generated=True, mode_name= "play")
                        if not model:
                            self.current_state = "HOME"
                            break

                        game_scene_ui(self.stdscr, model, context)
                        save_player(model.player)
                        handle_post_game_scene_save(self.stdscr, model)
                        continue



                    # 3) A string => existing map filename
                    if isinstance(selection, str):
                        filename = selection
                        model, context = build_model_common(filename, is_generated=False, mode_name = "play")
                        if not model:
                            self.current_state = "HOME"
                            break

                        game_scene_ui(self.stdscr, model, context)
                        save_player(model.player)
                        handle_post_game_scene_save(self.stdscr, model)

            elif self.current_state == "SETTINGS":
                settings_scene_ui(self.stdscr)
                self.current_state = "HOME"

            elif self.current_state == "QUIT":
                self.running = False