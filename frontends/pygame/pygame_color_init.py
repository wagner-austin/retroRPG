# File: pygame_color_init.py
# version: 1.0
#
# Summary: Provides a centralized color management system for pygame.
#          Defines base colors and helper functions to parse color pair strings.
#
# Tags: colors, pygame, setup

# Base colors as RGB tuples.
COLORS = {
    "black":      (0, 0, 0),
    "red":        (255, 0, 0),
    "green":      (0, 255, 0),
    "yellow":     (255, 255, 0),
    "blue":       (0, 0, 255),
    "magenta":    (255, 0, 255),
    "cyan":       (0, 255, 255),
    "white":      (255, 255, 255),
    "light_gray": (180, 180, 180),
    "dark_gray":  (80, 80, 80)
}

def get_color(color_name):
    """
    Returns the RGB tuple for a given color name.
    If not found, defaults to white.
    """
    return COLORS.get(color_name.lower(), COLORS["white"])

#seems archaic. plan to remove eventually.
def parse_color_pair(pair_str):
    """
    Parses a string like 'white_on_black' and returns a tuple (foreground, background)
    of RGB tuples. If parsing fails, defaults to white on black.
    """
    try:
        fg_str, bg_str = pair_str.lower().split("_on_")
        return get_color(fg_str), get_color(bg_str)
    except ValueError:
        return get_color(pair_str), get_color("black")

def get_foreground(pair_str):
    """
    Returns the foreground color (RGB tuple) from a color pair string (e.g., 'white_on_black').
    """
    fg, _ = parse_color_pair(pair_str)
    return fg