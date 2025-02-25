# File: pygame_scene_home.py
# version: 1.5.0 (updated to remove legacy curses rendering)
#
# Summary:
#   Defines HomeScene using plugin layers: a base erase layer, a background art layer,
#   a menu layer, and a title layer.
#
#   The layout and fonts are scaled dynamically.
#
#   The input handler has been modified so that:
#     - 'v' toggles debug mode.
#     - Arrow keys (or 'w' and 's') move the selection.
#     - ENTER/SPACE returns the currently selected option.
#     - Direct selection via keys:
#         * '1' or 'p' returns 1.
#         * '2' returns 2.
#         * '3', 'q', or ESCAPE returns 3.
#
# Tags: scene, home, menu, pygame

import pygame
from .pygame_scene_base import Scene
from .pygame_scene_layer_base import SceneLayer
from .where_pygame_themes_lives import CURRENT_THEME
from .pygame_utils import (
    draw_text,         # Renamed from safe_addstr to reflect pygame-only drawing.
    update_cell_sizes,
    get_scaled_font,
    get_scaled_value
)

###############################################################################
# Base Erase Layer
###############################################################################
class PygameBaseEraseLayer(SceneLayer):
    def __init__(self, z_index=0):
        super().__init__(name="base_erase_layer", z_index=z_index)

    def draw(self, renderer, dt, context):
        screen = renderer.get_surface()
        # Fill the entire screen with black.
        screen.fill((0, 0, 0))
        # Legacy (curses-style) clear code commented out:
        # screen.fill((0, 0, 0))  # [LEGACY]

###############################################################################
# Frame Art Layer (Background Art)
###############################################################################
class PygameFrameArtLayer(SceneLayer):
    def __init__(self, art_key="main_menu_art", z_index=100):
        super().__init__(name=f"frame_art_{art_key}", z_index=z_index)
        self.art_key = art_key
        self.border_color = (0, 100, 200)
        self.border_thickness = 4  # Base thickness; will be scaled.

    def _draw_art(self, screen, art_lines, start_row=2, start_col=2):
        """Draws a list of ASCII art lines onto the screen."""
        row = start_row
        for line in art_lines:
            # Use the pygame draw_text helper (replacing legacy safe_addstr)
            draw_text(screen, row, start_col, line, (255, 255, 255))
            row += 1

    def draw(self, renderer, dt, context):
        screen = renderer.get_surface()
        w, h = screen.get_size()
        # Compute a scaled border thickness.
        thickness = max(1, get_scaled_value(self.border_thickness))
        pygame.draw.rect(screen, self.border_color, (0, 0, w, h), thickness)
        # Get art lines from the current theme.
        art_lines = CURRENT_THEME.get(self.art_key, [])
        if art_lines:
            self._draw_art(screen, art_lines, start_row=2, start_col=2)

###############################################################################
# Home Title Layer
###############################################################################
class PygameHomeTitleLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="home_title", z_index=500)
        self.base_font_size = 40
        self.title_text = "Welcome to RetroRPG!"
        self.title_color = (0, 255, 0)

    def draw(self, renderer, dt, context):
        screen = renderer.get_surface()
        # Dynamically scale the font.
        font = get_scaled_font(self.base_font_size, bold=True)
        text_surface = font.render(self.title_text, True, self.title_color)
        pos_x = get_scaled_value(50)
        pos_y = get_scaled_value(30)
        screen.blit(text_surface, (pos_x, pos_y))

###############################################################################
# Home Menu Layer
###############################################################################
class PygameHomeMenuLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="home_menu", z_index=400)
        self.menu_lines = [
            "1) Play",
            "2) Settings",
            "3) Quit"
        ]
        self.current_select_slot = 0  # index into selectable menu items
        self.base_font_size = 24

    def draw(self, renderer, dt, context):
        screen = renderer.get_surface()
        font = get_scaled_font(self.base_font_size)
        line_height = font.get_linesize()
        w, h = screen.get_size()
        start_y = h - (len(self.menu_lines) * line_height) - get_scaled_value(20)
        y = start_y
        pos_x = get_scaled_value(50)
        for i, text in enumerate(self.menu_lines):
            color = (255, 255, 0) if i == self.current_select_slot else (200, 200, 200)
            surf = font.render(text, True, color)
            screen.blit(surf, (pos_x, y))
            y += line_height

    def move_selection_up(self):
        self.current_select_slot = max(0, self.current_select_slot - 1)

    def move_selection_down(self):
        self.current_select_slot = min(len(self.menu_lines) - 1, self.current_select_slot + 1)

    def get_current_choice(self):
        # Return the menu option (1-based) corresponding to the current selection.
        return self.current_select_slot + 1

###############################################################################
# Home Scene
###############################################################################
class HomeScene(Scene):
    def __init__(self):
        super().__init__()
        # Use shared layers; legacy code is commented out below.
        # from .layer_presets import BaseEraseLayer, FrameArtLayer  # [LEGACY]
        self.base_layer  = PygameBaseEraseLayer(z_index=0)
        self.bg_layer    = PygameFrameArtLayer("main_menu_art", z_index=100)
        self.menu_layer  = PygameHomeMenuLayer()
        self.title_layer = PygameHomeTitleLayer()
        # The layer order:
        #   Base background (z_index 0)
        #   Background art (z_index 100)
        #   Menu (z_index 400)
        #   Title (z_index 500)
        self.layers = [
            self.base_layer,
            self.bg_layer,
            self.menu_layer,
            self.title_layer,
        ]

    def handle_input(self, event):
        """
        Process a full pygame event.
        Returns:
          1 for Play, 2 for Settings, 3 for Quit.
          
        The logic is:
          - Toggle debug mode with 'v'.
          - Arrow keys (or 'w' and 's') move the selection.
          - ENTER or SPACE returns the currently highlighted option.
          - Direct selection via keys:
              * '1' or 'p' returns 1.
              * '2' returns 2.
              * '3', 'q', or ESCAPE returns 3.
        """
        if event.type == pygame.KEYDOWN:
            # Toggle debug mode if 'v' is pressed.
            if event.key in (pygame.K_v,):
                import tools.debug as debug
                debug.toggle_debug()
                return None

            # Use arrow keys (or 'w' and 's') to move the selection.
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu_layer.move_selection_up()
                return None
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_layer.move_selection_down()
                return None

            # ENTER or SPACE returns the currently highlighted option.
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.menu_layer.get_current_choice()

            # Direct selection via keys:
            elif event.key in (pygame.K_1, pygame.K_p):
                return 1
            elif event.key in (pygame.K_2,):
                return 2
            elif event.key in (pygame.K_3, pygame.K_q, pygame.K_ESCAPE):
                return 3

        return None