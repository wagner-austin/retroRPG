# File: pygame_scene_load.py
# version: 2.5
#
# Summary:
#   Defines LoadScene – a plugin‐based scene for loading or generating a map.
#   The scene uses layered drawing:
#       - Base background (lowest) for clearing/filling the screen.
#       - Background art (frame and theme art) above the base.
#       - Global effects (if any) from the global effects manager.
#       - Map list (z_index=400)
#       - Header (title and instructions, z_index=500)
#
# Tags: map, load, scene

import pygame
import tools.debug as debug
from .pygame_scene_base import Scene
from .pygame_scene_layer_base import SceneLayer
from .pygame_common import draw_title, draw_instructions
from .where_pygame_themes_lives import CURRENT_THEME
from .pygame_utils import draw_text  # our modern drawing helper
from .pygame_color_init import get_foreground  # returns foreground RGB tuple
from .pygame_selector_highlight import draw_global_selector_line

from map_system.map_list_logic import get_map_list, delete_map_file

class LoadHeaderLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="load_header", z_index=500)

    def draw(self, renderer, dt, context):
        screen = renderer.screen
        draw_title(screen, "Load Map", row=1)
        instructions = [
            "↑/↓ = select, ENTER = load, 'd' = del, 'q' = back, 'v' = dbg"
        ]
        draw_instructions(screen, instructions, from_bottom=3)

class LoadMenuLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="load_menu", z_index=400)
        self.options = ["Generate a new map"]
        maps = get_map_list(extension=".json")
        self.options.extend(maps)
        self.current_index = 0
        self.frame_count = 0

    def draw(self, renderer, dt, context):
        screen = renderer.screen
        max_w, max_h = screen.get_size()  # (width, height)
        row = 10  # Start drawing options at grid row 10.
        for i, option in enumerate(self.options):
            display_text = option if i == 0 else f"{i}) {option}"
            is_selected = (i == self.current_index)
            draw_global_selector_line(
                screen,
                row,
                f"> {display_text}" if is_selected else f"  {display_text}",
                is_selected=is_selected,
                frame=self.frame_count
            )
            row += 1
        self.frame_count += 1

    def handle_key(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            self.current_index = max(0, self.current_index - 1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.current_index = min(len(self.options) - 1, self.current_index + 1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.current_index == 0:
                return "GENERATE"
            else:
                return self.options[self.current_index]
        elif key in (pygame.K_q, pygame.K_ESCAPE):
            return ""  # Cancel and return to main menu.
        elif key == pygame.K_v:
            debug.toggle_debug()
        elif key == pygame.K_d:
            if self.current_index > 0:
                to_delete = self.options[self.current_index]
                confirm = prompt_delete_confirmation(to_delete)
                if confirm:
                    success = delete_map_file(to_delete)
                    if success:
                        del self.options[self.current_index]
                        if self.current_index >= len(self.options):
                            self.current_index = len(self.options) - 1
        elif key >= pygame.K_0 and key <= pygame.K_9:
            typed = key - pygame.K_0
            if 0 <= typed < len(self.options):
                self.current_index = typed
        return None

class LoadScene(Scene):
    def __init__(self):
        super().__init__()
        from .pygame_layer_presets import BaseEraseLayer, FrameArtLayer
        self.base_layer = BaseEraseLayer()
        self.bg_layer = FrameArtLayer("crocodile_art", z_index=100)
        self.menu_layer = LoadMenuLayer()
        self.header_layer = LoadHeaderLayer()
        self.layers = [self.base_layer, self.bg_layer, self.menu_layer, self.header_layer]

    def handle_input(self, event):
        """
        Accepts a full pygame event. If the event is KEYDOWN,
        passes event.key to the menu_layer handler.
        """
        if event.type == pygame.KEYDOWN:
            result = self.menu_layer.handle_key(event.key)
            if result is not None:
                return result
        return None

def prompt_delete_confirmation(filename):
    """
    Displays a confirmation prompt for deleting a map.
    Returns True if confirmed, False otherwise.
    """
    screen = pygame.display.get_surface()
    max_w, max_h = screen.get_size()
    question = f"Delete '{filename}'? (y/n)"
    from .pygame_utils import CELL_WIDTH, CELL_HEIGHT, draw_text
    grid_cols = max_w // CELL_WIDTH
    grid_rows = max_h // CELL_HEIGHT
    row = grid_rows - 2
    blank_line = " " * (grid_cols - 4)
    from .pygame_color_init import get_foreground
    attr = get_foreground(CURRENT_THEME["confirmation_color"])
    draw_text(screen, row, 2, blank_line, attr, clip=True)
    draw_text(screen, row, 2, question, attr, clip=True)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key in (pygame.K_n, pygame.K_q, pygame.K_ESCAPE):
                    return False