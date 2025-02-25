# FileName: pygame_game_renderer.py
# version: 4.2 (updated with get_surface() for dynamic use)
# Summary: A pygame-based renderer implementing IGameRenderer.
#          Renders scene layers and provides access to the main display surface.
# Tags: pygame, ui, renderer

import pygame
from engine.engine_interfaces import IGameRenderer

class PygameGameRenderer(IGameRenderer):
    def __init__(self, screen):
        """
        Initialize the renderer with the given pygame Surface.
        """
        self.screen = screen
        self.map_top_offset = 3
        self.map_side_offset = 0

        # Hide the mouse cursor for a cleaner UI.
        pygame.mouse.set_visible(False)

    def get_surface(self):
        """
        Returns the underlying pygame Surface.
        This method is used by scene layers to obtain the drawing surface.
        """
        return self.screen

    def get_visible_size(self):
        """
        Returns the visible size of the screen (in pixels) minus any offsets.
        """
        width, height = self.screen.get_size()
        visible_rows = height - self.map_top_offset
        if visible_rows < 0:
            visible_rows = 0
        visible_cols = width - self.map_side_offset
        return (visible_cols, visible_rows)

    def render_scene(self, scene, dt=0, context=None):
        """
        Renders a Scene object that provides .get_layers().
        """
        # Clear the screen (fill with black).
        self.screen.fill((0, 0, 0))

        # Retrieve scene layers.
        layers = scene.get_layers()

        # Sort layers by their z_index.
        layers_sorted = sorted(layers, key=lambda layer: layer.z_index)

        # Draw each layer (lowest z_index drawn first).
        for layer in layers_sorted:
            layer.draw(self, dt, context)

        # Update the display.
        pygame.display.flip()