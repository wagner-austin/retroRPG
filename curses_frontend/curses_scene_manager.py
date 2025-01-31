# FileName: curses_scene_manager.py
# version: 3.2 (now prompts y/n to save if leaving a newly generated map)
#
# Summary: Contains the high-level MenuFlowManager class that organizes
#          the main menu screens (HOME, SETTINGS, PLAY, EDIT).
#          Uses 'play_runner' purely for building the model,
#          calls 'curses_scene_game.game_scene_ui' for curses I/O,
#          then adds a y/n save prompt if the map was newly generated.
#
# Tags: scene, menu, manager

import os
import json
import curses  # needed for user input in the prompt method

from .curses_scene_home import home_scene_ui
from .curses_scene_settings import settings_scene_ui
from .curses_scene_load import load_scene_ui
from .curses_scene_game import game_scene_ui
from .curses_scene_save import save_map_ui

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
    actual gameplay/editor usage. If the map is new, we prompt y/n to save.
    Finally, we update the player's data or map file if needed, then
    return to the main menu or quit.
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
                # Keep letting the user pick a map or "Generate new" until they cancel
                while True:
                    selection = load_scene_ui(self.stdscr)
                    if not selection:
                        # user canceled => back to main menu
                        self.current_state = "HOME"
                        break

                    # 1) "Generate new map" => special string "GENERATE"
                    if selection == "GENERATE":
                        model, context = build_model_for_play({}, is_generated=True)
                        if not model:
                            self.current_state = "HOME"
                            break

                        game_scene_ui(self.stdscr, model, context)
                        save_player(model.player)

                        # If brand new, prompt user y/n to save
                        self._post_game_scene_save(model)
                        continue

                    # 2) If we got a dict => newly generated (procedural) map
                    if isinstance(selection, dict):
                        model, context = build_model_for_play(selection, is_generated=True)
                        if not model:
                            self.current_state = "HOME"
                            break

                        game_scene_ui(self.stdscr, model, context)
                        save_player(model.player)

                        # If brand new, prompt user y/n to save
                        self._post_game_scene_save(model)
                        continue

                    # 3) A tuple => user wants Editor mode
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

                        game_scene_ui(self.stdscr, model, context)
                        save_player(model.player)

                        # If brand new, prompt user y/n to save
                        self._post_game_scene_save(model)

                        # If it was an existing file, update the JSON with new x,y
                        if action_type == "EDIT" and model.loaded_map_filename:
                            self._update_player_coords_in_map(
                                model.loaded_map_filename,
                                model.player.x,
                                model.player.y
                            )
                        continue

                    # 4) Otherwise, it's a string => a filename (existing map)
                    filename = selection
                    model, context = build_model_for_play(filename, is_generated=False)
                    if not model:
                        self.current_state = "HOME"
                        break

                    game_scene_ui(self.stdscr, model, context)
                    save_player(model.player)

                    # If brand new, prompt user y/n to save (rare, but in theory possible)
                    self._post_game_scene_save(model)

                    # If we loaded from an actual file, store new x,y
                    if model.loaded_map_filename:
                        self._update_player_coords_in_map(
                            model.loaded_map_filename,
                            model.player.x,
                            model.player.y
                        )
                # Done handling all "PLAY" cycles

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

    def _post_game_scene_save(self, model):
        """
        If 'model' has no 'loaded_map_filename', it means it's a new map.
        Prompt the user whether to save. If yes, show the standard save UI.
        If no, do nothing (skip) and return to the load screen (next iteration).
        """
        is_new = (model.loaded_map_filename is None)
        if is_new:
            # Prompt user "Save new map? (y/n)" at bottom of screen
            wants_save = self._prompt_save_new_map()
            if wants_save:
                # Proceed with standard save UI
                placed_scenery = getattr(model, 'placed_scenery', {})
                w = getattr(model, 'width', 100)
                h = getattr(model, 'height', 100)
                save_map_ui(
                    self.stdscr,
                    placed_scenery=placed_scenery,
                    player=model.player,
                    world_width=w,
                    world_height=h,
                    filename_override=None,  # user picks or creates a name
                    notify_overwrite=False
                )
            # If user says no, we skip saving and go back to the load scene
            # (the 'while True' will continue -> calls load_scene_ui again)
        else:
            # If it's an existing file, no special prompt is needed.
            # The user might still have the auto "save_map_ui" for existing
            # maps, if you want that logic. But in the current code, we only
            # auto-update x,y in the file.
            pass

    def _prompt_save_new_map(self):
        """
        Displays a yes/no prompt at the bottom: "Save new map? (y/n)"
        Returns True if user selects 'y', False if 'n' or ESC.
        """
        max_h, max_w = self.stdscr.getmaxyx()
        question = "Save new map? (y/n)"
        row = max_h - 2
        col = 2

        # Prepare the screen for input
        self.stdscr.nodelay(False)
        curses.curs_set(1)
        curses.echo()

        # Clear the line
        blank_line = " " * (max_w - 4)
        self.stdscr.addstr(row, col, blank_line)
        self.stdscr.move(row, col)
        self.stdscr.addstr(row, col, question)
        self.stdscr.refresh()

        while True:
            c = self.stdscr.getch()
            if c in (ord('y'), ord('Y')):
                self._restore_input_mode()
                return True
            elif c in (ord('n'), ord('N'), ord('q'), 27):  # ESC or n => no
                self._restore_input_mode()
                return False

    def _restore_input_mode(self):
        """
        Return terminal to a no-echo, no-cursor, non-blocking mode.
        """
        curses.noecho()
        curses.curs_set(0)
        curses.napms(50)
        curses.flushinp()
        self.stdscr.nodelay(True)