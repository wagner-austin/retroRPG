# FileName: curses_scene_manager.py
# version: 3.6
#
# Summary: High-level MenuFlowManager for main menu screens (HOME, SETTINGS, GAME).
#          Ensures both player data (inventory) and map changes (scenery, player_x/y)
#          are saved when returning from an existing map.
#
# Tags: scene, menu, manager

import os
import json
import curses  # needed for user input
from .curses_scene_home import home_scene_ui
from .curses_scene_settings import settings_scene_ui
from .curses_scene_load import load_scene_ui
from .curses_scene_game import game_scene_ui
from .curses_scene_save import save_map_ui

from .curses_color_init import init_colors
from curses_frontend.curses_controls_ui import prompt_yes_no
from player_char_io import save_player
from map_io_storage import save_map_file
from play_runner import (
    build_model_for_play,
    build_model_for_editor
)

class MenuFlowManager:
    """
    Manages the main menu screens (HOME, SETTINGS, GAME).
    After the user leaves the game scene, we ensure that:
     - The player's data is always saved to player.json.
     - If it’s an existing map, we also update map JSON with player x,y (optionally)
       and prompt to save newly placed/removed scenery.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr

        # Initialize curses colors right at the start
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
                else:             # Settings
                    self.current_state = "SETTINGS"

            elif self.current_state == "PLAY":
                while True:
                    selection = load_scene_ui(self.stdscr)
                    if not selection:
                        self.current_state = "HOME"
                        break

                    # 1) "GENERATE" => new map
                    if selection == "GENERATE":
                        model, context = build_model_for_play({}, is_generated=True)
                        if not model:
                            self.current_state = "HOME"
                            break
                        game_scene_ui(self.stdscr, model, context)

                        # Always save player data after game scene
                        save_player(model.player)
                        self._post_game_scene_save(model)
                        continue

                    # 2) If we got a dict => newly generated
                    if isinstance(selection, dict):
                        model, context = build_model_for_play(selection, is_generated=True)
                        if not model:
                            self.current_state = "HOME"
                            break
                        game_scene_ui(self.stdscr, model, context)

                        save_player(model.player)
                        self._post_game_scene_save(model)
                        continue

                    # 3) A tuple => Editor mode
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
                        self._post_game_scene_save(model)
                        continue

                    # 4) Otherwise, it’s an existing map filename
                    filename = selection
                    model, context = build_model_for_play(filename, is_generated=False)
                    if not model:
                        self.current_state = "HOME"
                        break
                    game_scene_ui(self.stdscr, model, context)

                    save_player(model.player)
                    self._post_game_scene_save(model)
                # done with the 'PLAY' loop

            elif self.current_state == "SETTINGS":
                settings_scene_ui(self.stdscr)
                self.current_state = "HOME"

            elif self.current_state == "QUIT":
                self.running = False

    def _update_player_coords_in_map(self, filename, px, py):
        """
        Helper to store player's final x,y into an existing map file (JSON).
        If you also want to store gold, wood, etc., add them as well, e.g.:
            data["player_gold"] = ...
        """
        maps_dir = "maps"
        map_path = os.path.join(maps_dir, filename)
        if not os.path.exists(map_path):
            return
        try:
            with open(map_path, "r") as f:
                data = json.load(f)

            # Update coordinates in map
            data["player_x"] = px
            data["player_y"] = py

            save_map_file(map_path, data)
        except:
            pass

    def _post_game_scene_save(self, model):
        """
        If it's a brand-new map (model.loaded_map_filename is None), prompt "Save new map? (y/n)".
        If it's an existing map (model.loaded_map_filename is not None):
          1) Update that map JSON with player's final x,y
          2) Prompt "Save changes to existing map? (y/n)" => if yes, overwrite the map file
        Also re-save the player's data (just in case).
        """
        # ALWAYS save player data again, if needed
        save_player(model.player)
        

        # brand-new map => ask user to save under new file name
        if model.loaded_map_filename is None:
            wants_save = self._prompt_save_new_map()
            if wants_save:
                placed_scenery = getattr(model, 'placed_scenery', {})
                w = getattr(model, 'width', 100)
                h = getattr(model, 'height', 100)
                save_map_ui(
                    self.stdscr,
                    placed_scenery=placed_scenery,
                    player=model.player,
                    world_width=w,
                    world_height=h,
                    filename_override=None,
                    notify_overwrite=False
                )
        else:
            self._update_player_coords_in_map(
            model.loaded_map_filename,
            model.player.x,
            model.player.y
            )
            
            placed_scenery = getattr(model, 'placed_scenery', {})
            w = getattr(model, 'width', 100)
            h = getattr(model, 'height', 100)
            save_map_ui(
                self.stdscr,
                placed_scenery=placed_scenery,
                player=model.player,
                world_width=w,
                world_height=h,
                filename_override=model.loaded_map_filename,
                notify_overwrite=False
                )


            # Then ask user if they want to save changes (placed scenery, etc.)
            changes_saved = prompt_yes_no(
                None,  # no direct renderer needed
                "Save changes to existing map? (y/n)"
            )
            if changes_saved:
                placed_scenery = getattr(model, 'placed_scenery', {})
                w = getattr(model, 'width', 100)
                h = getattr(model, 'height', 100)
                # Overwrite the same file with the updated scenery
                save_map_ui(
                    self.stdscr,
                    placed_scenery=placed_scenery,
                    player=model.player,
                    world_width=w,
                    world_height=h,
                    filename_override=model.loaded_map_filename,
                    notify_overwrite=False
                )

    def _prompt_save_new_map(self):
        """
        Displays "Save new map? (q/n)" at the bottom. 'q' => yes, 'n'/ESC => no.
        Returns True if user picks 'q', else False.
        """
        max_h, max_w = self.stdscr.getmaxyx()
        question = "Save new map? (y/n)"
        row = max_h - 2
        col = 2

        self.stdscr.nodelay(False)
        curses.curs_set(1)
        curses.echo(0)

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
            elif c in (ord ('q'), ord ('Q'), ord('n'), ord('N'), 27):
                self._restore_input_mode()
                return False

    def _restore_input_mode(self):
        curses.noecho()
        curses.curs_set(0)
        curses.napms(50)
        curses.flushinp()
        self.stdscr.nodelay(True)