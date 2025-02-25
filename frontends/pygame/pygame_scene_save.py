# File: pygame_scene_save.py
# version: 2.1
#
# Summary:
#   Contains all save‐scene UI flows for picking/creating filenames,
#   prompting for overwrites, and calling the logic to store map data.
#
# Tags: map, save, scene

import pygame
import tools.debug as debug
from map_system.map_list_logic import get_map_list
from .pygame_utils import draw_text, update_cell_sizes
from .pygame_common import draw_title, draw_instructions
from .where_pygame_themes_lives import CURRENT_THEME
from map_system.scene_save_logic import (
    save_player_data,
    does_file_exist_in_maps_dir,
    build_and_save_map,
    update_player_coords_in_map
)
from .pygame_scene_base import Scene
from .pygame_scene_layer_base import SceneLayer
from .pygame_game_renderer import PygameGameRenderer

class SaveHeaderLayer(SceneLayer):
    def __init__(self):
        super().__init__(name="save_header", z_index=500)

    def draw(self, renderer, dt, context):
        screen = renderer.screen
        draw_title(screen, "Save Map", row=1)
        instructions = ["Select a map to overwrite, 'n' for new, ENTER to cancel, 'v' toggles debug"]
        draw_instructions(screen, instructions, from_bottom=3)

class SaveMenuLayer(SceneLayer):
    def __init__(self, files):
        super().__init__(name="save_menu", z_index=400)
        self.files = files
        self.current_index = 0

    def draw(self, renderer, dt, context):
        screen = renderer.screen
        max_w, max_h = screen.get_size()
        row = 10
        from .pygame_color_init import get_foreground
        attr_prompt = get_foreground(CURRENT_THEME["prompt_color"])
        attr_menu_item = get_foreground(CURRENT_THEME["menu_item_color"])
        if self.files:
            draw_text(screen, row, 2, "Maps (pick number to overwrite) or 'n' for new, or ENTER to cancel:", attr_prompt, clip=True)
            row += 1
            for i, filename in enumerate(self.files, start=1):
                indicator = ">" if (i - 1) == self.current_index else " "
                draw_text(screen, row, 2, f"{indicator} {i}. {filename}", attr_menu_item, clip=True)
                row += 1
            draw_text(screen, row, 2, "Enter choice or press ENTER to cancel:", attr_prompt, clip=True)
        else:
            draw_text(screen, row, 2, "No existing maps. Press 'n' for new, 'v' toggles debug, or ENTER to cancel:", attr_prompt, clip=True)

    def handle_key(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            self.current_index = max(0, self.current_index - 1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.current_index = min(len(self.files) - 1, self.current_index + 1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.files:
                return self.files[self.current_index]
            else:
                return ""
        elif key in (pygame.K_n,):
            return "NEW_FILE"
        elif key in (pygame.K_v,):
            debug.toggle_debug()
        elif pygame.K_0 <= key <= pygame.K_9:
            digit = key - pygame.K_0
            if 1 <= digit <= len(self.files):
                return self.files[digit - 1]
        return None

class SaveScene(Scene):
    """
    Plugin-based scene for saving maps.
    Returns a filename (string) if an existing file is selected,
    "NEW_FILE" if the user chooses to create a new file,
    or an empty string if cancelled.
    """
    def __init__(self):
        super().__init__()
        files = get_map_list(extension=".json")
        from .pygame_layer_presets import BaseEraseLayer, FrameArtLayer
        self.base_layer = BaseEraseLayer()
        self.background_layer = FrameArtLayer("crocodile_art", z_index=100)
        self.menu_layer = SaveMenuLayer(files)
        self.header_layer = SaveHeaderLayer()
        self.layers = [self.base_layer, self.background_layer, self.menu_layer, self.header_layer]

    def handle_input(self, key):
        result = self.menu_layer.handle_key(key)
        if result is not None:
            return result
        return None

def run_save_scene(screen):
    renderer = PygameGameRenderer(screen)
    update_cell_sizes(screen)  # Update UI scaling at startup.
    dt = 0
    save_scene = SaveScene()
    while True:
        renderer.render_scene(save_scene, dt=dt, context=None)
        dt += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.FULLSCREEN | pygame.RESIZABLE)
                update_cell_sizes(screen)
            elif event.type == pygame.KEYDOWN:
                result = save_scene.handle_input(event.key)
                if result is not None:
                    return result

def prompt_for_filename(screen, prompt):
    """
    Displays a prompt on screen and collects a string from the user.
    This is a simple blocking text input loop.
    """
    renderer = PygameGameRenderer(screen)
    row = 10
    from .pygame_color_init import get_foreground
    attr = get_foreground(CURRENT_THEME["prompt_color"])
    input_str = ""
    done = False

    while not done:
        draw_text(screen, row, 2, " " * 50, attr, clip=True)  # Clear the input line.
        draw_text(screen, row, 2, prompt + " " + input_str, attr, clip=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    done = True
                    break
                elif event.key == pygame.K_BACKSPACE:
                    input_str = input_str[:-1]
                else:
                    input_str += event.unicode
    return input_str.strip()

def _restore_input_mode(screen):
    # In pygame, no special restoration is required.
    pass

def save_map_ui(screen, placed_scenery, player=None, world_width=100, world_height=100,
                filename_override=None, notify_overwrite=False):
    if filename_override:
        filename = filename_override
    else:
        overwrite_or_new = run_save_scene(screen)
        if not overwrite_or_new:
            return
        if overwrite_or_new == "NEW_FILE":
            filename = prompt_for_filename(screen, "Enter filename to save as:")
            if not filename:
                return
            if not filename.endswith(".json"):
                filename += ".json"
        else:
            filename = overwrite_or_new

    file_existed = does_file_exist_in_maps_dir(filename)
    build_and_save_map(filename, placed_scenery, player, world_width, world_height)
    if file_existed and notify_overwrite:
        pygame.time.delay(0)
    # Transition back to HomeScene is handled by the MenuFlowManager.

def prompt_yes_no(screen, question):
    """
    Displays a yes/no question and waits for a key press.
    Returns True if the user presses 'y' (or 'Y'), else False.
    """
    renderer = PygameGameRenderer(screen)
    width, height = screen.get_size()
    row = height // 20  # Adjust as needed for your grid.
    col = 2
    blank_line = " " * 50
    from .pygame_color_init import get_foreground
    draw_text(screen, row, col, blank_line, get_foreground("white_on_black"), clip=True)
    draw_text(screen, row, col, question, get_foreground("white_on_black"), clip=True)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                else:
                    return False

def handle_post_game_scene_save(screen, model):
    """
    Called after the player returns from the game scene.
    Determines whether to save a new map or update an existing one,
    then calls the save UI flow.
    """
    save_player_data(model.player)
    if model.loaded_map_filename is None:
        wants_save = prompt_yes_no(screen, "Save new map? (y/n)")
        if wants_save:
            placed_scenery = getattr(model, 'placed_scenery', {})
            w = getattr(model, 'world_width', 100)
            h = getattr(model, 'world_height', 100)
            save_map_ui(screen,
                        placed_scenery=placed_scenery,
                        player=model.player,
                        world_width=w,
                        world_height=h,
                        filename_override=None,
                        notify_overwrite=False)
    else:
        update_player_coords_in_map(model.loaded_map_filename, model.player.x, model.player.y)
        placed_scenery = getattr(model, 'placed_scenery', {})
        w = getattr(model, 'world_width', 100)
        h = getattr(model, 'world_height', 100)
        save_map_ui(screen,
                    placed_scenery=placed_scenery,
                    player=model.player,
                    world_width=w,
                    world_height=h,
                    filename_override=model.loaded_map_filename,
                    notify_overwrite=False)