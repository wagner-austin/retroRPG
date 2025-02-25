# File: pygame_utils.py
# version: 1.6.0
#
# Summary: Provides pygame UI helpers for display setup, dynamic scaling, font rendering,
#          and grid-based drawing. All UI properties (resolution, font, scaling) are configured here.
#
# Tags: pygame, utils, ui

import time
import pygame
import shutil
from typing import Tuple

# Initialize pygame's font module.
pygame.font.init()

# ---------------------------
# Global UI Configuration
# ---------------------------
UI_CONFIG = {
    'base_resolution': (800, 600),   # Baseline resolution for scaling.
    'base_font_size': 30,            # Baseline font size (in pixels).
    'scale_factor': 1.0,             # Computed at runtime.
    'default_font': None             # None uses pygame's default font; otherwise, specify a TTF file.
}

# Initialize the default font and compute cell dimensions.
DEFAULT_FONT = pygame.font.Font(UI_CONFIG['default_font'], UI_CONFIG['base_font_size'])
CELL_WIDTH, CELL_HEIGHT = DEFAULT_FONT.size("W")  # Use "W" as a representative character.

# ---------------------------
# Display Helpers
# ---------------------------
def create_display():
    """
    Creates and returns a resizable full-screen display using the base resolution.
    """
    return pygame.display.set_mode(UI_CONFIG['base_resolution'], pygame.FULLSCREEN | pygame.RESIZABLE)

def update_cell_sizes(screen):
    """
    Updates the global DEFAULT_FONT and cell dimensions based on the current screen resolution.
    Should be called when the display is created or resized.
    """
    global DEFAULT_FONT, CELL_WIDTH, CELL_HEIGHT, UI_CONFIG
    width, height = screen.get_size()
    base_width, base_height = UI_CONFIG['base_resolution']
    scale = min(width / base_width, height / base_height)
    UI_CONFIG['scale_factor'] = scale
    new_font_size = max(12, int(UI_CONFIG['base_font_size'] * scale))
    DEFAULT_FONT = pygame.font.Font(UI_CONFIG['default_font'], new_font_size)
    CELL_WIDTH, CELL_HEIGHT = DEFAULT_FONT.size("W")

def get_scaled_value(value: int) -> int:
    """
    Returns the given value scaled by the current UI scale factor.
    """
    return int(value * UI_CONFIG['scale_factor'])

def get_scaled_font(base_size: int, bold: bool = False) -> pygame.font.Font:
    """
    Returns a pygame Font object scaled by the current UI scale factor.
    """
    new_font_size = max(12, int(base_size * UI_CONFIG['scale_factor']))
    font = pygame.font.Font(UI_CONFIG['default_font'], new_font_size)
    font.set_bold(bold)
    return font

# ---------------------------
# Drawing Helpers (Grid-based)
# ---------------------------
def draw_text(screen, row: int, col: int, text: str, color: Tuple[int, int, int], clip: bool = False) -> None:
    """
    Draws text on the given screen at grid coordinates (row, col) using DEFAULT_FONT.
    If clip is True, the text is truncated to fit within the grid width.
    """
    screen_width, _ = screen.get_size()
    grid_cols = screen_width // CELL_WIDTH
    if clip:
        available_chars = grid_cols - col
        text = text[:available_chars]
    text_surface = DEFAULT_FONT.render(text, True, color)
    screen.blit(text_surface, (col * CELL_WIDTH, row * CELL_HEIGHT))

def draw_character(screen, row: int, col: int, ch: str, color: Tuple[int, int, int]) -> None:
    """
    Draws a single character on the given screen at grid coordinates (row, col) using DEFAULT_FONT.
    """
    draw_text(screen, row, col, str(ch), color, clip=True)

# ---------------------------
# Terminal Size Helper (Optional)
# ---------------------------
def get_terminal_size() -> Tuple[int, int]:
    """
    Returns the terminal size as (columns, lines) using shutil.get_terminal_size().
    Useful as a fallback.
    """
    try:
        ts = shutil.get_terminal_size()
        return (ts.columns, ts.lines)
    except Exception:
        print("Unable to get terminal size; defaulting to 80x24.")
        time.sleep(10)
        return (80, 24)