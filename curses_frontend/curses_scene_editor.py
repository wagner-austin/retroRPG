# FileName: curses_scene_editor.py
# version: 1.0
#
# Summary: Renders an overlay at the top of the screen when the editor is active,
#          showing the currently selected scenery item and minimal controls.
#
# Tags: editor, overlay, ui

import curses
from .curses_utils import safe_addstr, get_color_attr
from .where_curses_themes_lives import CURRENT_THEME

def draw_editor_overlay(stdscr, model):
    """
    Draw a small overlay at the top if the editor is active,
    showing the currently selected item and short controls help.
    """

    # 1) Check if editor is enabled
    if not model or not model.context.enable_editor_commands:
        return

    # 2) Safety: if there's no editor list or index out of range, skip
    editor_list = model.editor_scenery_list
    idx = model.editor_scenery_index
    if not editor_list or idx < 0 or idx >= len(editor_list):
        return

    # 3) Get the current definition ID
    current_def_id = editor_list[idx][0]  # The first element in your (def_id, _, _) tuple

    # 4) Build overlay text (customize as you like)
    overlay_text = (
        f"[EDITOR MODE] Selected: {current_def_id}  "
        "(p=place, x=remove top, l=next, k=prev, u=undo, e=exit editor)"
    )

    # 5) Choose a color from the theme
    overlay_color = CURRENT_THEME["text_color"]  # e.g., "white_on_black"
    overlay_attr = get_color_attr(overlay_color)

    # 6) Draw near the top (row=1 or row=0)
    max_h, max_w = stdscr.getmaxyx()
    row = 1
    col = 2

    # Clear the line first so leftover text doesn't remain
    blank_line = " " * (max_w - 4)
    safe_addstr(stdscr, row, 1, blank_line, overlay_attr, clip_borders=False)

    # Now draw the overlay text
    safe_addstr(stdscr, row, col, overlay_text, overlay_attr, clip_borders=False)