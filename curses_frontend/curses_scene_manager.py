# FileName: curses_scene_manager.py
# version: 3.0 (refactored)
#
# Summary: Contains the high-level MenuFlowManager class that organizes
#          the main menu screens (HOME, SETTINGS, PLAY, EDIT).
#          Now uses 'play_runner' purely for building the model,
#          then calls 'curses_scene_game.game_scene_ui' to do curses I/O,
#          and finally saves state as needed.
#
# Tags: scene, menu, manager

#import curses
#import debug
import os
import json

from .curses_scene_home import home_scene_ui
from .curses_scene_settings import settings_scene_ui
from .curses_scene_load import load_scene_ui
from .curses_scene_game import game_scene_ui
from player_char_io import save_player
from map_io_storage import save_map_file
from play_runner import (
    build_model_for_play,
    build_model_for_editor
)


class MenuFlowManager:
    """
    A controller that organizes the main menu screens (HOME, SETTINGS, GAME).
    The GAME flow loads or generates a map, then calls game_scene_ui(...) for
    actual gameplay/editor usage. Finally, we update the player's data or map file
    if needed, then return to the main menu or quit.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
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
                else:             # Settings
                    self.current_state = "SETTINGS"

            elif self.current_state == "PLAY":
                # Keep letting the user pick a map or “Generate new” until they cancel
                while True:
                    selection = load_scene_ui(self.stdscr)
                    if not selection:
                        # user canceled => back to main menu
                        self.current_state = "HOME"
                        break

                    # 1) “Generate new map” (returned the special string "GENERATE")
                    if selection == "GENERATE":
                        model, context = build_model_for_play({}, is_generated=True)
                        if not model:
                            self.current_state = "HOME"
                            break
                        game_scene_ui(self.stdscr, model, context)
                        # Save the player after the loop
                        save_player(model.player)
                        # No file to update since it's a brand-new procedural map
                        continue

                    # 2) If we got back a dict (the generator returned a raw dict)
                    if isinstance(selection, dict):
                        model, context = build_model_for_play(selection, is_generated=True)
                        if not model:
                            self.current_state = "HOME"
                            break
                        game_scene_ui(self.stdscr, model, context)
                        save_player(model.player)
                        continue

                    # 3) If we get a tuple => user wants Editor mode
                    if isinstance(selection, tuple):
                        action_type, actual_map = selection
                        if action_type == "EDIT_GENERATE":
                            model, context = build_model_for_editor({}, is_generated=True)
                        elif action_type == "EDIT":
                            model, context = build_model_for_editor(actual_map, is_generated=False)
                        else:
                            self.current_state = "HOME"
                            break

                        if not model:
                            self.current_state = "HOME"
                            break

                        # Run the editor “scene”
                        game_scene_ui(self.stdscr, model, context)
                        # Save the player after the loop
                        save_player(model.player)

                        # If it was an existing file, update the JSON with new x,y
                        if action_type == "EDIT" and model.loaded_map_filename:
                            self._update_player_coords_in_map(
                                model.loaded_map_filename,
                                model.player.x,
                                model.player.y
                            )
                        continue

                    # 4) Otherwise, it's a string => a filename
                    filename = selection
                    model, context = build_model_for_play(filename, is_generated=False)
                    if not model:
                        self.current_state = "HOME"
                        break

                    game_scene_ui(self.stdscr, model, context)
                    save_player(model.player)

                    # If we loaded from an actual file, store new x,y
                    if model.loaded_map_filename:
                        self._update_player_coords_in_map(
                            model.loaded_map_filename,
                            model.player.x,
                            model.player.y
                        )

                # Done handling all “PLAY” cycles

            elif self.current_state == "SETTINGS":
                settings_scene_ui(self.stdscr)
                self.current_state = "HOME"

            elif self.current_state == "QUIT":
                self.running = False

    def _update_player_coords_in_map(self, filename, px, py):
        """
        Helper to store player's final x,y into an existing map file (JSON).
        """
        maps_dir = "maps"
        map_path = os.path.join(maps_dir, filename)
        if not os.path.exists(map_path):
            return
        try:
            with open(map_path, "r") as f:
                data = json.load(f)
            data["player_x"] = px
            data["player_y"] = py
            save_map_file(map_path, data)
        except:
            pass