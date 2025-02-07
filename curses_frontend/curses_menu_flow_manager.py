# FileName: curses_menu_flow_manager.py
# version: 4.1
#
# Summary:
#   High-level MenuFlowManager for main menu screens (HOME, SETTINGS, PLAY).
#   Uses plugin-based scenes. Global effect layers (e.g. snow and rain) are applied
#   automatically to every scene via the base Scene class.
#
# Tags: scene, menu, manager

import time
from .curses_color_init import init_colors

# Import plugin-based scene classes
from .curses_scene_home import HomeScene
from .curses_scene_settings import SettingsScene
from .curses_scene_load import LoadScene
from .curses_scene_game import GameScene

# Import dedicated save logic
from .curses_scene_save import handle_post_game_scene_save

from map_model_builder import build_model_common
from procedural_map_generator.map_generator_pipeline import create_procedural_model

# Import the renderer for scenes
from .curses_game_renderer import CursesGameRenderer

# Import global effects manager and effect layers (aggregated in one place)
from .global_effects_manager import add_effect_layer
from .curses_effect_layers import SnowEffectLayer, RainEffectLayer

class MenuFlowManager:
    """
    Manages the main menu screens (HOME, SETTINGS, PLAY).
    Global effect layers are automatically applied to every scene.
    """
    def __init__(self, stdscr):
        self.stdscr = stdscr
        init_colors()
        self.current_state = "HOME"
        self.running = True

        # Add global effect layers once. These will be included in every scene.
        add_effect_layer(SnowEffectLayer(num_flakes=10, color_name="green_on_black"))
        add_effect_layer(RainEffectLayer(num_drops=10, color_name="blue_on_black", direction="down"))

    def run_scene(self, scene):
        """
        Render the given scene in a loop until it returns a menu choice.
        """
        renderer = CursesGameRenderer(self.stdscr)
        dt = 0
        while True:
            renderer.render_scene(scene, dt=dt, context=None)
            dt += 1
            key = self.stdscr.getch()
            if key != -1:
                choice = scene.handle_input(key)
                if choice is not None:
                    return choice

    def run(self):
        while self.running:
            if self.current_state == "HOME":
                # Use the plugin-based HomeScene.
                home_scene = HomeScene()
                user_choice = self.run_scene(home_scene)
                if user_choice == 1:  # Play
                    self.current_state = "PLAY"
                elif user_choice == 2:  # Quit
                    self.current_state = "QUIT"
                elif user_choice == 3:  # Settings
                    self.current_state = "SETTINGS"
            elif self.current_state == "PLAY":
                # Use the plugin-based LoadScene to select or generate a map.
                load_scene = LoadScene()
                selection = self.run_scene(load_scene)
                if not selection:
                    # User canceled map selection; return to HOME.
                    self.current_state = "HOME"
                    continue

                # 1) If selection is "GENERATE", create a brand-new map.
                if selection == "GENERATE":
                    model, context = create_procedural_model()
                    if not model:
                        self.current_state = "HOME"
                        continue
                    game_scene = GameScene(model, context)
                    _ = game_scene.run(self.stdscr)
                    handle_post_game_scene_save(self.stdscr, model)
                    continue

                # 2) If selection is a dict (new map data).
                if isinstance(selection, dict):
                    time.sleep(10)  # Legacy debug pause.
                    model, context = build_model_common(selection, is_generated=True, mode_name="play")
                    if not model:
                        self.current_state = "HOME"
                        continue
                    game_scene = GameScene(model, context)
                    _ = game_scene.run(self.stdscr)
                    handle_post_game_scene_save(self.stdscr, model)
                    continue

                # 3) If selection is a string (existing map filename).
                if isinstance(selection, str):
                    model, context = build_model_common(selection, is_generated=False, mode_name="play")
                    if not model:
                        self.current_state = "HOME"
                        continue
                    game_scene = GameScene(model, context)
                    _ = game_scene.run(self.stdscr)
                    handle_post_game_scene_save(self.stdscr, model)
            elif self.current_state == "SETTINGS":
                settings_scene = SettingsScene()
                _ = self.run_scene(settings_scene)
                self.current_state = "HOME"
            elif self.current_state == "QUIT":
                self.running = False

# Legacy functions (such as home_scene_ui, load_scene_ui, game_scene_ui) have been commented out.