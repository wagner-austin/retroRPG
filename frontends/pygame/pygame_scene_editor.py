# File: pygame_scene_editor.py
# version: 1.0
#
# Summary: Renders an overlay at the top of the screen when the editor is active,
#          showing the currently selected scenery item and minimal controls.
#
# Tags: editor, overlay, ui

from .pygame_utils import safe_addstr, get_color_attr
from .where_pygame_themes_lives import CURRENT_THEME

def draw_editor_overlay(screen, model):
    """
    Draw a small overlay at the top if the editor is active,
    showing the currently selected item and short controls help.
    """
    if not model or not model.context.enable_editor_commands:
        return
    editor_list = model.editor_scenery_list
    idx = model.editor_scenery_index
    if not editor_list or idx < 0 or idx >= len(editor_list):
        return
    current_def_id = editor_list[idx][0]
    overlay_text = (
        f"[EDITOR MODE] Selected: {current_def_id}  "
        "(p=place, x=remove top, l=next, k=prev, u=undo, e=exit editor)"
    )
    overlay_color = CURRENT_THEME["text_color"]
    overlay_attr = get_color_attr(overlay_color)
    
    # In pygame, screen.get_size() returns (width, height)
    max_w, max_h = screen.get_size()
    
    # For grid-based text layout, we assume safe_addstr converts grid (row, col)
    # into pixel coordinates; here, we use a row of 1 and a column offset of 2.
    row = 1
    col = 2
    # Create a blank line that spans nearly the entire width.
    blank_line = " " * (max_w - 4)
    
    safe_addstr(screen, row, 1, blank_line, overlay_attr, clip_borders=False)
    safe_addstr(screen, row, col, overlay_text, overlay_attr, clip_borders=False)
