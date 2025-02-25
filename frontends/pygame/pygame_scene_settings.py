# File: pygame_scene_settings.py
# version: 2.4 (updated to use shared layers and standardized text colors)
#
# Summary:
#   Defines the SettingsScene using plugin layers.
#   The scene uses layered drawing:
#       - Base background (lowest) for clearing/filling the screen.
#       - Background art (using shared art drawing) above the base.
#       - Global effects (if any) from the global effects manager.
#       - Menu (z_index=400) and Title (z_index=500) on top.
#
# Tags: scene, settings

import pygame
import tools.debug as debug
from .pygame_scene_base import Scene
from .pygame_scene_layer_base import SceneLayer
from .pygame_common import draw_title
from .pygame_selector_highlight import draw_global_selector_line

class SettingsTitleLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="settings_title", z_index=500)

    def draw(self, renderer, dt, context):
        screen = renderer.screen
        draw_title(screen, "Settings (Placeholder)", row=1)

class SettingsMenuLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="settings_menu", z_index=400)
        self.menu_lines = [
            "1) Toggle Debug",
            "2) Return"
        ]
        self.current_select_slot = 0

    def draw(self, renderer, dt, context):
        screen = renderer.screen
        max_w, max_h = screen.get_size()
        start_row = 4
        row = start_row
        for i, line in enumerate(self.menu_lines):
            is_selected = (i == self.current_select_slot)
            draw_global_selector_line(
                screen, row, line,
                is_selected=is_selected,
                frame=dt  # Use dt as the frame count for animation effects.
            )
            row += 1

    def handle_key(self, key):
        if key == pygame.K_v:
            debug.toggle_debug()
        if key in (pygame.K_UP, pygame.K_w):
            self.current_select_slot = max(0, self.current_select_slot - 1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.current_select_slot = min(len(self.menu_lines) - 1, self.current_select_slot + 1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.current_select_slot == 0:
                debug.toggle_debug()
                return None
            elif self.current_select_slot == 1:
                return "QUIT"
        return None

class SettingsScene(Scene):
    def __init__(self):
        super().__init__()
        from .pygame_layer_presets import BaseEraseLayer, FrameArtLayer
        self.base_layer = BaseEraseLayer()
        self.background_layer = FrameArtLayer("crocodile_art", z_index=100)
        self.menu_layer = SettingsMenuLayer()
        self.title_layer = SettingsTitleLayer()
        self.layers = [self.base_layer, self.background_layer, self.menu_layer, self.title_layer]

    def handle_input(self, key):
        result = self.menu_layer.handle_key(key)
        if result is not None:
            return result
        if key in (pygame.K_q, pygame.K_ESCAPE):
            return "QUIT"
        return None
