# FileName: curses_menu_flow_manager.py
# version: 3.8
#
# Summary: High-level MenuFlowManager for main menu screens (HOME, SETTINGS, GAME).
#          Defers map-saving logic to curses_scene_save.
# 
# Changelog:
#  - Updated to use create_procedural_model from map_generator_pipeline
#  - Commented out old "GENERATE" code that built an empty map
#
# Tags: scene, menu, manager

import time
from .curses_scene_home import home_scene_ui
from .curses_scene_settings import settings_scene_ui
from .curses_scene_load import load_scene_ui
from .curses_scene_game import game_scene_ui
from .curses_color_init import init_colors

# We now import the dedicated save logic from curses_scene_save
from .curses_scene_save import handle_post_game_scene_save

# Removed direct save_player import (still used in handle_post_game_scene_save if needed)
from map_model_builder import build_model_common

# NEW: import the single pipeline helper
from procedural_map_generator.map_generator_pipeline import create_procedural_model


class MenuFlowManager:
    """
    Manages the main menu screens (HOME, SETTINGS, GAME).
    After the user leaves the game scene, we ensure that:
     - The player's data is always saved to player.json (handled in handle_post_game_scene_save).
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
                        # user canceled => go back to HOME
                        self.current_state = "HOME"
                        break

                    # 1) "GENERATE" => brand-new map
                    if selection == "GENERATE":
                        # Use our new single-pipeline helper
                        model, context = create_procedural_model()
                        if not model:
                            self.current_state = "HOME"
                            break

                        game_scene_ui(self.stdscr, model, context)
                        handle_post_game_scene_save(self.stdscr, model)
                        continue


                    # 2) A dictionary => newly generated map data from somewhere else
                    if isinstance(selection, dict):
                        print ("curses_flow_menuanager")
                        time.sleep(10)
                        model, context = build_model_common(selection, is_generated=True, mode_name="play")
                        if not model:
                            self.current_state = "HOME"
                            break

                        game_scene_ui(self.stdscr, model, context)
                        handle_post_game_scene_save(self.stdscr, model)
                        continue

                    # 3) A string => existing map filename
                    if isinstance(selection, str):
                        filename = selection
                        model, context = build_model_common(filename, is_generated=False, mode_name="play")
                        if not model:
                            self.current_state = "HOME"
                            break

                        game_scene_ui(self.stdscr, model, context)
                        handle_post_game_scene_save(self.stdscr, model)

            elif self.current_state == "SETTINGS":
                settings_scene_ui(self.stdscr)
                self.current_state = "HOME"

            elif self.current_state == "QUIT":
                self.running = False