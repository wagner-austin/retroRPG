# File: pygame_common.py
# version: 2.12 (updated to include _draw_art)
#
# Summary: Provides higher-level drawing helpers for frames, titles, instructions,
#          styled text, and art. Uses unified pygame_utils and pygame_color_init for
#          rendering text, colors, and themes.
#
# Tags: ui, rendering, pygame

import pygame
import tools.debug as debug
from .pygame_utils import draw_text, draw_character, CELL_WIDTH, CELL_HEIGHT
from .pygame_color_init import get_foreground, get_color
from .where_pygame_themes_lives import CURRENT_THEME

def _draw_art(screen, art_lines, start_row=1, start_col=2):
    """
    Renders a list of ASCII art lines starting at grid position (start_row, start_col)
    using the 'ascii_art_color' from the current theme.
    """
    ascii_art_color = CURRENT_THEME.get("ascii_art_color", "white_on_black")
    fg_color = get_foreground(ascii_art_color)
    grid_rows = screen.get_height() // CELL_HEIGHT
    row = start_row
    for line in art_lines:
        if row >= grid_rows - 1:
            break
        draw_text(screen, row, start_col, line, fg_color, clip=True)
        row += 1

def draw_title(screen, text, row=1, color_name=None):
    """
    Draws a title string at the given grid row.
    If color_name is not provided, uses CURRENT_THEME's 'title_color'.
    """
    if color_name is None:
        color_name = CURRENT_THEME["title_color"]
    fg_color = get_foreground(color_name)
    draw_text(screen, row, 2, text, fg_color, clip=True)

def draw_instructions(screen, lines, from_bottom=2, color_name=None):
    """
    Draws a list of instruction lines near the bottom of the screen.
    If color_name is not provided, uses CURRENT_THEME's 'instructions_color'.
    """
    if color_name is None:
        color_name = CURRENT_THEME["instructions_color"]
    screen_height = screen.get_height()
    grid_rows = screen_height // CELL_HEIGHT
    fg_color = get_foreground(color_name)
    start_row = grid_rows - from_bottom - len(lines)
    if start_row < 1:
        start_row = 1
    row = start_row
    for line in lines:
        draw_text(screen, row, 2, line, fg_color, clip=True)
        row += 1

def draw_screen_frame(screen, color_name=None):
    """
    Draws a rectangular border around the entire screen and a "Debug mode" label if enabled.
    If color_name is not provided, uses CURRENT_THEME's 'border_color'.
    """
    if color_name is None:
        color_name = CURRENT_THEME["border_color"]
    max_w, max_h = screen.get_size()
    border_color = get_foreground(color_name)
    pygame.draw.rect(screen, border_color, pygame.Rect(0, 0, max_w, max_h), 1)
    if debug.DEBUG_CONFIG.get("enabled", False):
        label = "Debug mode: On"
        font = pygame.font.Font(None, 24)
        dbg_color = get_foreground("white_on_black")
        text_surface = font.render(label, True, dbg_color)
        label_width = text_surface.get_width()
        x = max_w - label_width - 6
        y = 0
        screen.blit(text_surface, (x, y))

def draw_styled_text(screen, row, col, text, fg="white", bg=None, font_size=24, bold=False):
    """
    Draws text at grid position (row, col) using pygame's native font rendering.
    
    Parameters:
      - fg: Foreground color (as a friendly name or an RGB tuple).
      - bg: Optional background color (if None, rendered transparently).
      - font_size: The size of the font.
      - bold: Whether to render the text in bold.
    """
    fg_color = get_color(fg) if isinstance(fg, str) else fg
    bg_color = get_color(bg) if (bg and isinstance(bg, str)) else bg
    font = pygame.font.Font(None, font_size)
    font.set_bold(bold)
    text_surface = font.render(text, True, fg_color, bg_color)
    x = col * CELL_WIDTH
    y = row * CELL_HEIGHT
    screen.blit(text_surface, (x, y))

def draw_inside_frame_ch(screen, row, col, ch, attr):
    """
    Draws a single character at grid coordinates (row, col) if within frame boundaries.
    """
    max_w, max_h = screen.get_size()
    grid_cols = max_w // CELL_WIDTH
    grid_rows = max_h // CELL_HEIGHT
    if 1 <= row < grid_rows - 1 and 1 <= col < grid_cols - 1:
        draw_character(screen, row, col, ch, attr)