# File: pygame_selector_highlight.py
# version: 1.5
#
# Summary: Provides a globally configurable highlight/selector system for pygame.
#          This system modifies text colors for selected text using pygame's native rendering.
#
# Tags: selector, highlight, effects, pygame

import pygame
from .pygame_utils import draw_text
from .pygame_color_init import get_foreground
from .where_pygame_themes_lives import CURRENT_THEME

GLOBAL_HIGHLIGHT_CONFIG = {
    # These are set to None so that CURRENT_THEME values will be used at runtime.
    "selected_color_name":   None,
    "unselected_color_name": None,
    "effect_name":           "REVERSE_BLINK",
    "speed_factor":          5,
}

def get_global_selector_config():
    """
    Returns the global highlight configuration, filling in selected/unselected
    color names from CURRENT_THEME if they are None.
    """
    config = GLOBAL_HIGHLIGHT_CONFIG.copy()
    if config["selected_color_name"] is None:
        config["selected_color_name"] = CURRENT_THEME["highlight_selected_color"]
    if config["unselected_color_name"] is None:
        config["unselected_color_name"] = CURRENT_THEME["highlight_unselected_color"]
    return config

def invert_color(color):
    """
    Inverts an RGB color.
    """
    return (255 - color[0], 255 - color[1], 255 - color[2])

def get_selector_effect_color(effect="REVERSE_BLINK", base_color=(255, 255, 255), frame=0, speed_factor=10):
    """
    Mimics selector effect attributes by modifying the base_color.
    For some effects, the color will alternate between the base color and its inversion.
    """
    toggle_state = (frame // speed_factor) % 2
    if effect == "NONE":
        return base_color
    elif effect == "REVERSE":
        return invert_color(base_color)
    elif effect == "BLINK":
        # Blink effect could alternate with no effect; here we simply return base_color.
        return base_color
    elif effect == "REVERSE_BLINK":
        return invert_color(base_color) if toggle_state else base_color
    elif effect == "FLASH":
        return invert_color(base_color) if toggle_state == 0 else base_color
    elif effect == "GLOW":
        return base_color  # Glow effect not implemented
    elif effect == "SHIMMER":
        return invert_color(base_color) if toggle_state == 0 else base_color
    return base_color

def draw_global_selector_line(screen, row: int, text: str, is_selected: bool=False, frame: int=0) -> None:
    """
    Draws a text line at a given grid row using the global selector configuration.
    When selected, the text color is modified by the specified effect.
    """
    config = get_global_selector_config()
    selected_color_name   = config["selected_color_name"]
    unselected_color_name = config["unselected_color_name"]
    effect_name           = config["effect_name"]
    speed_factor          = config["speed_factor"]

    if is_selected:
        base_color = get_foreground(selected_color_name)
        modified_color = get_selector_effect_color(effect=effect_name, base_color=base_color,
                                                   frame=frame, speed_factor=speed_factor)
    else:
        modified_color = get_foreground(unselected_color_name)

    # Draw the text at grid row 'row' and column 2.
    draw_text(screen, row, 2, text, modified_color)