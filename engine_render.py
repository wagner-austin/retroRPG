# FileName: engine_render.py
# version: 1.1
# Unified "dirty tile" tracking and partial/delta rendering logic here.

import curses
from scenery_main import (
    _get_objects_at,
    get_scenery_color_at
)

def mark_dirty(model, x, y):
    """
    Mark a tile as 'dirty' (needing redraw) if in valid bounds.
    """
    if 0 <= x < model.world_width and 0 <= y < model.world_height:
        model.dirty_tiles.add((x, y))

def draw_tile(stdscr, tx, ty,
              player,
              placed_scenery,
              camera_x, camera_y,
              map_top_offset,
              action_flash_info=None):
    sx = tx - camera_x
    sy = ty - camera_y + map_top_offset

    max_scr_rows, max_scr_cols = stdscr.getmaxyx()
    if not (0 <= sx < max_scr_cols and map_top_offset <= sy < max_scr_rows):
        return

    stack = _get_objects_at(placed_scenery, tx, ty)
    top_obj = stack[-1] if stack else None

    # If topmost is '§' => might hide the player
    hiding_obj = top_obj if (top_obj and top_obj.char == '§') else None

    flash_active = False
    if action_flash_info:
        fx, fy, count = action_flash_info
        if (tx, ty) == (fx, fy) and count > 0:
            flash_active = True

    char_to_draw = " "
    color_id = 0

    if top_obj:
        char_to_draw = top_obj.char
        color_id = top_obj.color_pair

    # If player is here
    if (player.x, player.y) == (tx, ty):
        if hiding_obj:
            # '§' hides the player
            char_to_draw = '§'
            color_id = 7
        else:
            # Player visible
            tile_color = get_scenery_color_at(tx, ty, placed_scenery)
            # Let certain tile colors override the usual
            if tile_color in (4, 5, 8):
                color_id = tile_color
            else:
                color_id = 9
            char_to_draw = player.char

    if flash_active:
        color_id = 10  # e.g. a flash color

    try:
        stdscr.addstr(sy, sx, char_to_draw, curses.color_pair(color_id))
    except:
        pass

def update_partial_tiles_in_view(stdscr,
                                 player,
                                 placed_scenery,
                                 camera_x, camera_y,
                                 map_top_offset,
                                 dirty_tiles,
                                 action_flash_info=None,
                                 world_width=100,
                                 world_height=60):
    """
    Re-draw just the 'dirty' tiles in the visible region (partial/delta render).
    """
    max_scr_rows, max_scr_cols = stdscr.getmaxyx()
    visible_cols = max_scr_cols
    visible_rows = max_scr_rows - map_top_offset

    for (wx, wy) in dirty_tiles:
        if (camera_x <= wx < camera_x + visible_cols and
            camera_y <= wy < camera_y + visible_rows):
            draw_tile(stdscr, wx, wy,
                      player,
                      placed_scenery,
                      camera_x,
                      camera_y,
                      map_top_offset,
                      action_flash_info=action_flash_info)

    stdscr.refresh()


def draw_layers(stdscr, model):
    """
    If you want multiple layers (e.g. parallax backgrounds, 
    separate UI overlays, etc.), do it here.
    For now, it's just a placeholder stub.
    """
    pass