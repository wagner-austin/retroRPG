# File: pygame_menu_flow_manager.py
# version: 4.9 (modernized)
#
# Summary:
#   High-level MenuFlowManager for main menu screens (HOME, SETTINGS, PLAY)
#   using pygame. Global effect layers are automatically applied to every scene.
#   Transitions between scenes are controlled solely by pygame_scene_transition.py.
#
# Tags: scene, menu, transition, pygame

import pygame
# Removed legacy import: from .pygame_color_init import init_colors
from .pygame_scene_home import HomeScene
from .pygame_scene_settings import SettingsScene
from .pygame_scene_load import LoadScene
from .pygame_scene_game import GameScene
from .pygame_scene_transition import run_transition
from .pygame_scene_save import handle_post_game_scene_save
from map_system.map_model_builder import build_model_common
from map_system.mapgen.map_generator_pipeline import create_procedural_model
from .pygame_game_renderer import PygameGameRenderer
from .pygame_global_effects_manager import add_effect_layer
from .pygame_effect_layers import SnowEffectLayer, RainEffectLayer
from .pygame_utils import update_cell_sizes  # UI scaling helper

class MenuFlowManager:
    """
    Manages the main menu screens using pygame.
    Global effect layers are automatically applied to every scene.
    """
    def __init__(self, screen):
        self.screen = screen
        # Removed legacy call to init_colors()
        self.current_state = "HOME"
        self.running = True

        # Add global effect layers.
        add_effect_layer(SnowEffectLayer(num_flakes=10, color_name="white_on_black"))
        add_effect_layer(RainEffectLayer(num_drops=10, color_name="blue_on_black", direction="down"))

    def run_scene(self, scene):
        """
        Renders the given scene in a loop until it returns a menu choice.
        """
        renderer = PygameGameRenderer(self.screen)
        clock = pygame.time.Clock()
        dt = 0

        while True:
            renderer.render_scene(scene, dt=dt, context=None)
            pygame.display.flip()
            dt += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.VIDEORESIZE:
                    # Recreate the screen as full screen and resizable.
                    self.screen = pygame.display.set_mode(event.size, pygame.FULLSCREEN | pygame.RESIZABLE)
                    # Update global font and cell sizes.
                    update_cell_sizes(self.screen)
                elif event.type == pygame.KEYDOWN:
                    choice = scene.handle_input(event)
                    if choice is not None:
                        return choice

            clock.tick(60)  # Limit to 60 FPS

    def run_transition(self, current_scene, next_scene):
        run_transition(self.screen, current_scene, next_scene)

    def run(self):
        """
        Main loop to manage transitions between scenes.
        """
        while self.running:
            if self.current_state == "HOME":
                home_scene = HomeScene()
                user_choice = self.run_scene(home_scene)
                if not self.running:
                    break

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
                if not self.running:
                    break

                if not selection:
                    self.run_transition(load_scene, HomeScene())
                    self.current_state = "HOME"
                    continue

                if selection == "GENERATE":
                    model, context = create_procedural_model()
                    if not model:
                        self.current_state = "HOME"
                        continue
                    game_scene = GameScene(model, context)
                    self.run_transition(load_scene, game_scene)
                    _ = game_scene.run(self.screen)
                    handle_post_game_scene_save(self.screen, model)
                    continue

                if isinstance(selection, dict):
                    model, context = build_model_common(selection, is_generated=True, mode_name="play")
                    if not model:
                        self.current_state = "HOME"
                        continue
                    game_scene = GameScene(model, context)
                    self.run_transition(load_scene, game_scene)
                    _ = game_scene.run(self.screen)
                    handle_post_game_scene_save(self.screen, model)
                    continue

                if isinstance(selection, str):
                    model, context = build_model_common(selection, is_generated=False, mode_name="play")
                    if not model:
                        self.current_state = "HOME"
                        continue
                    game_scene = GameScene(model, context)
                    self.run_transition(load_scene, game_scene)
                    _ = game_scene.run(self.screen)
                    handle_post_game_scene_save(self.screen, model)

            elif self.current_state == "QUIT":
                self.running = False