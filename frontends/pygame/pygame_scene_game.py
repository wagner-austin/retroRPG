# File: pygame_scene_game.py
# version: 2.0
#
# Summary:
#   Defines a GameScene that encapsulates the game loop.
#   This scene sets up the pygame‐based input and rendering,
#   and then calls run_game_loop from engine.engine_main.
#
#   Note: Because run_game_loop is a blocking call,
#         integration is not fully “non‑blocking” yet.
#
# Tags: scene, game

import pygame
from .pygame_scene_base import Scene
from .pygame_scene_layer_base import SceneLayer
from .pygame_game_renderer import PygameGameRenderer
from .pygame_input import PygameGameInput
from engine.engine_main import run_game_loop

class GameBackgroundLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="game_background", z_index=0)
    
    def draw(self, renderer, dt, context):
        # Optionally add extra background effects here.
        # For now, we leave this empty because run_game_loop handles full
        # drawing of the game world.
        pass

class GameOverlayLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="game_overlay", z_index=100)
    
    def draw(self, renderer, dt, context):
        # Here you could add HUD elements, inventory displays, or an editor overlay.
        pass

class GameScene(Scene):
    def __init__(self, model, context):
        super().__init__()
        self.model = model
        self.context = context
        # Setup plugin layers for additional overlays.
        self.background_layer = GameBackgroundLayer()
        self.overlay_layer = GameOverlayLayer()
        self.layers = [self.background_layer, self.overlay_layer]
    
    def run(self, screen):
        """
        Runs the game scene. Sets up input and rendering,
        then calls the main game loop.
        (run_game_loop is currently blocking.)
        """
        game_input = PygameGameInput()
        game_renderer = PygameGameRenderer(screen)
        
        # Delegate to the existing game loop.
        run_game_loop(self.model, self.context, game_input, game_renderer)
        
        # After the game loop exits, return a value or perform cleanup if needed.
        return "EXIT"

    def handle_input(self, key):
        # This method is not used since run_game_loop is blocking.
        pass