# FileName: curses_tile_render.py
# version: 1.1 (refactored to remove duplicate color-composition logic)
#
# Summary:
#   Contains common tile-drawing logic for the curses UI. Moved here from
#   curses_renderer.py to allow a cleaner separation of responsibilities.
#
# ChangeLog:
#   v1.1:  - Added `compose_fg_with_floor_bg` helper to remove repeated code.
#          - Updated `draw_single_tile` & `draw_player_on_top` to use helper.
#
# Tags: curses, ui, rendering

from .curses_utils import safe_addch, parse_two_color_names
from .curses_selector_highlight import get_color_attr
from scenery_defs import ALL_SCENERY_DEFS, TREE_TRUNK_ID, TREE_TOP_ID
from layer_defs import FLOOR_LAYER, OBJECTS_LAYER, ITEMS_LAYER, ENTITIES_LAYER


def compose_fg_with_floor_bg(floor_color_name, fg_object_color_name):
    """
    Given a floor color name (e.g. "white_on_black") and an object's
    foreground color name (e.g. "red_on_black"), combine them so that:
      - The object's foreground remains the same.
      - The background becomes whatever the floor's background was.
    Returns a curses color attribute.
    """
    fg_floor, bg_floor = parse_two_color_names(floor_color_name)
    fg_obj, _ = parse_two_color_names(fg_object_color_name)
    final_color_name = f"{fg_obj}_on_{bg_floor}"
    return get_color_attr(final_color_name)


def draw_single_tile(stdscr, wx, wy, sx, sy, model, blank_attr):
    """
    Draw the background/floor plus any objects, items, or entities for tile (wx, wy).
    Painted at screen coords (sx, sy). The player is NOT drawn here; that is handled
    separately to ensure the player remains above (or below) certain objects.
    """

    # Erase any leftover character first.
    safe_addch(stdscr, sy, sx, " ", blank_attr, clip_borders=True)

    tile_layers = model.placed_scenery.get((wx, wy), None)
    if not tile_layers:
        return

    # 1) Floor
    floor_obj = tile_layers.get(FLOOR_LAYER)
    floor_color_name = "white_on_black"
    if floor_obj:
        info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
        ch = info.get("ascii_char", floor_obj.char)
        floor_color_name = info.get("color_name", "white_on_black")
        floor_attr = get_color_attr(floor_color_name)
        safe_addch(stdscr, sy, sx, ch, floor_attr, clip_borders=True)

    # 2) Objects, Items, Entities in that order
    obj_list = (
        tile_layers.get(OBJECTS_LAYER, []) +
        tile_layers.get(ITEMS_LAYER, []) +
        tile_layers.get(ENTITIES_LAYER, [])
    )

    for obj in obj_list:
        info = ALL_SCENERY_DEFS.get(obj.definition_id, {})
        ch = info.get("ascii_char", obj.char)
        obj_color_name = info.get("color_name", "white_on_black")

        # If it's a TreeTop exactly where the player is, skip it here,
        # so we can handle the player and tree top ordering in draw_player_on_top().
        if obj.definition_id == TREE_TOP_ID and (wx, wy) == (model.player.x, model.player.y):
            continue

        # Combine floor BG and object FG to preserve floor's background color
        attr = compose_fg_with_floor_bg(floor_color_name, obj_color_name)
        safe_addch(stdscr, sy, sx, ch, attr, clip_borders=True)


def draw_player_on_top(stdscr, model, map_top_offset):
    """
    Draw the player above everything, but allow the tree trunk or top to
    draw last (so it can obscure the player if desired).

    If you want the player truly on top of all tiles, remove or modify
    the trunk-top pass at the end.
    """
    px = model.player.x - model.camera_x
    py = model.player.y - model.camera_y + map_top_offset
    max_h, max_w = stdscr.getmaxyx()

    if 0 <= px < max_w and 0 <= py < max_h:
        tile_layers = model.placed_scenery.get((model.player.x, model.player.y), {})

        # Determine the floor color for background merging
        floor_obj = tile_layers.get(FLOOR_LAYER)
        floor_color_name = "white_on_black"
        if floor_obj:
            finfo = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
            floor_color_name = finfo.get("color_name", "white_on_black")

        # Draw player with the floor-based background but player's chosen foreground
        player_fg = getattr(model.player, "color_name", "white")  # e.g. "cyan"
        player_char = getattr(model.player, "char", "@")          # e.g. '@'

        player_attr = compose_fg_with_floor_bg(floor_color_name, player_fg)
        safe_addch(stdscr, py, px, player_char, player_attr, clip_borders=True)

        # If there's a trunk/top in the same tile, it goes on top of the player
        objects_list = tile_layers.get(OBJECTS_LAYER, [])
        trunk_tops = [o for o in objects_list if o.definition_id in (TREE_TRUNK_ID, TREE_TOP_ID)]
        for t_obj in trunk_tops:
            info = ALL_SCENERY_DEFS.get(t_obj.definition_id, {})
            ch = info.get("ascii_char", t_obj.char)
            top_color = info.get("color_name", "white_on_black")

            trunk_attr = compose_fg_with_floor_bg(floor_color_name, top_color)
            safe_addch(stdscr, py, px, ch, trunk_attr, clip_borders=True)