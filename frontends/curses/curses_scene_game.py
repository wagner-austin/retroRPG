# File: curses_scene_game.py
# version: 2.0 (refactored to plugin architecture)
#
# Summary:
#   Defines a GameScene that encapsulates the game loop.
#   This scene sets up the curses‐based input and rendering,
#   and then calls run_game_loop from engine_main.
#
#   Note: Because the existing run_game_loop is a blocking call,
#         the integration is not fully “non‑blocking” yet.
#         In the future you might refactor engine_main.py to split updates
#         and rendering into per‑frame steps.
#
# Tags: scene, game

import curses
from .scene_base import Scene
from .scene_layer_base import SceneLayer
from .curses_game_renderer import CursesGameRenderer
from .where_curses_input_is_handled import CursesGameInput
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
        # For example, you might call a function such as:
        #   from .curses_scene_inventory import draw_inventory_summary
        #   draw_inventory_summary(renderer.stdscr, context, row=1, col=2)
        pass

class GameScene(Scene):
    def __init__(self, model, context):
        super().__init__()
        self.model = model
        self.context = context
        # Setup plugin layers (for future use) if you want to draw additional overlays.
        self.background_layer = GameBackgroundLayer()
        self.overlay_layer = GameOverlayLayer()
        self.layers = [self.background_layer, self.overlay_layer]
    
    def run(self, stdscr):
        """
        Run the game scene. This method sets up input and rendering,
        then calls the main game loop. (Currently, run_game_loop is blocking.)
        """
        # Setup the input and renderer as usual
        game_input = CursesGameInput(stdscr)
        game_renderer = CursesGameRenderer(stdscr)
        
        # (Optionally, before entering the game loop, you could draw your plugin layers.
        #  For example, you might call:
        #      for layer in self.get_layers():
        #          layer.draw(game_renderer, dt=0, context=self.context)
        #  so that any static overlays are drawn.)
        
        # Delegate to the existing game loop.
        # In the future, you might refactor run_game_loop to a per-frame update,
        # and then call update() and render() methods on your GameScene instance.
        run_game_loop(self.model, self.context, game_input, game_renderer)
        
        # After the game loop exits, return a value or perform cleanup if needed.
        return "EXIT"

    def handle_input(self, key):
        # This method would be used if you want non-blocking input handling
        # while in the game scene. Since run_game_loop is blocking, this is not used.
        pass

# Legacy function (deprecated):
#
# def game_scene_ui(stdscr, model, context):
#     game_input = CursesGameInput(stdscr)
#     game_renderer = CursesGameRenderer(stdscr)
#     run_game_loop(model, context, game_input, game_renderer)