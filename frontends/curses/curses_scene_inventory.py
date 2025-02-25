# FileName: curses_scene_inventory.py
# version: 1.1 (added draw_inventory_summary to unify inventory display)
#
# Summary: Dedicated screen to display the player's inventory (full) 
#          or a short summary of the player's inventory if needed.
#
# Tags: curses, ui, inventory

import curses
from .curses_common import draw_screen_frame, draw_title, draw_instructions
from .curses_utils import safe_addstr, get_color_attr
from .where_curses_themes_lives import CURRENT_THEME


def draw_inventory_summary(stdscr, model, row=1, col=2):
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

    safe_addstr(stdscr, row, col, inv_text, text_attr, clip_borders=True)


def show_inventory_screen(stdscr, model):
    """
    Shows the player's current inventory in a separate, blocking screen.
    Waits for any key to be pressed before returning.
    """
    stdscr.clear()
    draw_screen_frame(stdscr)

    # Optional: a title at the top
    draw_title(stdscr, "Inventory", row=1)

    # Build inventory text lines
    inventory_lines = [
        f"  Gold  = {model.player.gold}",
        f"  Wood  = {model.player.wood}",
        f"  Stone = {model.player.stone}"
    ]

    text_color = CURRENT_THEME["text_color"]
    text_attr = get_color_attr(text_color)

    row = 3
    for line in inventory_lines:
        safe_addstr(stdscr, row, 2, line, text_attr, clip_borders=True)
        row += 1

    # Provide consistent instructions near the bottom
    instructions = ["Press any key to return..."]
    draw_instructions(stdscr, instructions, from_bottom=2)

    stdscr.refresh()

    # Wait for a keypress
    stdscr.nodelay(False)
    curses.curs_set(0)
    stdscr.getch()
    stdscr.nodelay(True)