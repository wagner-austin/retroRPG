# File: curses_menu_flow_manager.py
# version: 4.8
#
# Summary:
#   High-level MenuFlowManager for main menu screens (HOME, SETTINGS, PLAY).
#   Uses plugin-based scenes. Global effect layers (e.g. snow and rain) are applied
#   automatically to every scene via the base Scene class.
#
#   Transitions between scenes are now completely controlled by curses_scene_transition.py.
#   The menu flow manager simply calls run_transition() with the current and next scenes.
#
#   This update adds a transition between the LoadScene and the GameScene (the actual map).
#
# Tags: scene, menu, manager, transition

from .curses_color_init import init_colors

# Import plugin-based scene classes
from .curses_scene_home import HomeScene
from .curses_scene_settings import SettingsScene
from .curses_scene_load import LoadScene
from .curses_scene_game import GameScene

# Import the transition helper from curses_scene_transition.py
from .curses_scene_transition import run_transition

# Import dedicated save logic
from .curses_scene_save import handle_post_game_scene_save

from map_system.map_model_builder import build_model_common
from map_system.mapgen.map_generator_pipeline import create_procedural_model

# Import the renderer for scenes
from .curses_game_renderer import CursesGameRenderer

# Import global effects manager and effect layers (aggregated in one place)
from .global_effects_manager import add_effect_layer
from .curses_effect_layers import SnowEffectLayer, RainEffectLayer

class MenuFlowManager:
    """
    Manages the main menu screens (HOME, SETTINGS, PLAY).
    Global effect layers are automatically applied to every scene.
    Transitions between scenes are now set solely by curses_scene_transition.py.
    """
    def __init__(self, stdscr):
        self.stdscr = stdscr
        init_colors()
        self.current_state = "HOME"
        self.running = True

        # Add global effect layers once.
        add_effect_layer(SnowEffectLayer(num_flakes=10, color_name="white_on_black"))
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

    def run_transition(self, current_scene, next_scene):
        """
        Calls the global run_transition() helper from curses_scene_transition.py.
        This helper reads all transition parameters from TRANSITION_CONFIG.
        """
        run_transition(self.stdscr, current_scene, next_scene)

    def run(self):
        while self.running:
            if self.current_state == "HOME":
                # Use the plugin-based HomeScene.
                home_scene = HomeScene()
                user_choice = self.run_scene(home_scene)
                if user_choice == 1:  # Play selected
                    load_scene = LoadScene()
                    self.run_transition(home_scene, load_scene)
                    self.current_state = "PLAY"
                elif user_choice == 2:  # Settings selected
                    settings_scene = SettingsScene()
                    self.run_transition(home_scene, settings_scene)
                    _ = self.run_scene(settings_scene)
                    self.run_transition(settings_scene, home_scene)
                    self.current_state = "HOME"
                elif user_choice == 3:  # Quit selected
                    self.current_state = "QUIT"
                    
            elif self.current_state == "PLAY":
                load_scene = LoadScene()
                selection = self.run_scene(load_scene)
                if not selection:
                    # User canceled map selection; transition from LoadScene to HomeScene.
                    self.run_transition(load_scene, HomeScene())
                    self.current_state = "HOME"
                    continue

                # For any valid selection (GENERATE, dict, or string),
                # create the GameScene and transition from the LoadScene into it.
                if selection == "GENERATE":
                    model, context = create_procedural_model()
                    if not model:
                        self.current_state = "HOME"
                        continue
                    game_scene = GameScene(model, context)
                    self.run_transition(load_scene, game_scene)
                    _ = game_scene.run(self.stdscr)
                    handle_post_game_scene_save(self.stdscr, model)
                    continue

                if isinstance(selection, dict):
                    model, context = build_model_common(selection, is_generated=True, mode_name="play")
                    if not model:
                        self.current_state = "HOME"
                        continue
                    game_scene = GameScene(model, context)
                    self.run_transition(load_scene, game_scene)
                    _ = game_scene.run(self.stdscr)
                    handle_post_game_scene_save(self.stdscr, model)
                    continue

                if isinstance(selection, str):
                    model, context = build_model_common(selection, is_generated=False, mode_name="play")
                    if not model:
                        self.current_state = "HOME"
                        continue
                    game_scene = GameScene(model, context)
                    self.run_transition(load_scene, game_scene)
                    _ = game_scene.run(self.stdscr)
                    handle_post_game_scene_save(self.stdscr, model)
            # The dedicated SETTINGS branch has been removed to avoid duplicate transitions.
            elif self.current_state == "QUIT":
                self.running = False

# Legacy functions (such as home_scene_ui, load_scene_ui, game_scene_ui) have been commented out.