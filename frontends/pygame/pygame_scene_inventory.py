# File: pygame_scene_inventory.py
# version: 1.1 (added draw_inventory_summary to unify inventory display)
#
# Summary:
#   Dedicated functions to display the player's inventory—either a brief summary
#   (for in-game overlays) or a full inventory screen that waits for a key press.
#
# Tags: pygame, ui, inventory

import pygame
from .pygame_common import draw_screen_frame, draw_title, draw_instructions
from .pygame_utils import safe_addstr, get_color_attr
from .where_pygame_themes_lives import CURRENT_THEME


def draw_inventory_summary(screen, model, row=1, col=2):
    """
    Draws a single-line summary of the player's inventory.
    Called by the main renderer when not in editor mode.
    """
    text_color = CURRENT_THEME["text_color"]
    text_attr = get_color_attr(text_color)
    inv_text = (
        f"Inventory: Gold={model.player.gold}, "
        f"Wood={model.player.wood}, Stone={model.player.stone}"
    )
    safe_addstr(screen, row, col, inv_text, text_attr, clip_borders=True)


def show_inventory_screen(screen, model):
    """
    Shows the player's current inventory in a separate, blocking screen.
    Waits for any key to be pressed before returning.
    """
    screen.fill((0, 0, 0))
    draw_screen_frame(screen)
    draw_title(screen, "Inventory", row=1)

    inventory_lines = [
        f"  Gold  = {model.player.gold}",
        f"  Wood  = {model.player.wood}",
        f"  Stone = {model.player.stone}"
    ]

    text_color = CURRENT_THEME["text_color"]
    text_attr = get_color_attr(text_color)

    row = 3
    for line in inventory_lines:
        safe_addstr(screen, row, 2, line, text_attr, clip_borders=True)
        row += 1

    instructions = ["Press any key to return..."]
    draw_instructions(screen, instructions, from_bottom=2)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                waiting = False
