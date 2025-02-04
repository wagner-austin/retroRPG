# FileName: curses_tile_drawing.py
# version: 1.2 (refactored to remove layer_for_def_id usage in rendering)
#
# Summary:
#   Contains common tile-drawing logic for the curses UI. Moved here from
#   curses_renderer.py to allow a cleaner separation of responsibilities.
#
# ChangeLog:
#   v1.1:  - Added `compose_fg_with_floor_bg` helper to remove repeated code.
#          - Updated `draw_single_tile` & `draw_player_on_top` to use helper.
#   v1.2:  - Now draws floor + other layers from layer_manager.get_layers_in_draw_order().
#          - The old code referencing layer_for_def_id is commented out.
#
# Tags: curses, ui, rendering

from .curses_utils import safe_addch, parse_two_color_names
from .curses_selector_highlight import get_color_attr

# We still need ALL_SCENERY_DEFS for char/color lookups.
from scenery_data.scenery_manager import ALL_SCENERY_DEFS

# NEW: import the layer order helper so we can draw in ascending z-index
from layer_manager import get_layers_in_draw_order

# If you have special logic for "TreeTop" or "TreeTrunk", you might import them:
# from scenery_placement_utils import TREE_TOP_ID, TREE_TRUNK_ID
# or just compare definition_id == "TreeTop"/"TreeTrunk" inline.

def compose_fg_with_floor_bg(floor_color_name, fg_object_color_name):
    """
    Given a floor color name (e.g. "white_on_black") and an object's
    foreground color name (e.g. "red_on_black"), combine them so that:
      - The object's foreground remains the same,
      - The background becomes whatever the floor's background was.
    Returns a curses color attribute (int).
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

    tile_dict = model.placed_scenery.get((wx, wy), None)
    if not tile_dict:
        return  # nothing to draw

    # ------------------------------------------------------
    # LEGACY CODE (commented out) that caused black-map issue:
    #
    # floor_obj = tile_layers.get(layer_for_def_id)
    # floor_color_name = "white_on_black"
    # if floor_obj:
    #     info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
    #     ch = info.get("ascii_char", floor_obj.char)
    #     floor_color_name = info.get("color_name", "white_on_black")
    #     floor_attr = get_color_attr(floor_color_name)
    #     safe_addch(stdscr, sy, sx, ch, floor_attr, clip_borders=True)
    #
    # obj_list = (
    #     tile_layers.get(layer_for_def_id, []) +
    #     tile_layers.get(layer_for_def_id, []) +
    #     tile_layers.get(layer_for_def_id, [])
    # )
    # for obj in obj_list: ...
    #
    # ------------------------------------------------------

    # NEW: multi-layer drawing approach
    # 1) Draw the floor first
    floor_obj = tile_dict.get("floor")
    floor_color_name = "white_on_black"

    if floor_obj:
        fdef = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
        ch_floor = fdef.get("ascii_char", floor_obj.char)
        floor_color_name = fdef.get("color_name", "white_on_black")
        floor_attr = get_color_attr(floor_color_name)
        safe_addch(stdscr, sy, sx, ch_floor, floor_attr, clip_borders=True)

    # 2) Draw every other layer in ascending z‐order,
    #    skipping "floor" because we already drew it above
    layers_in_order = get_layers_in_draw_order()
    for layer_name in layers_in_order:
        if layer_name == "floor":
            continue  # already handled

        # tile_dict might have e.g. tile_dict["objects"] = [...]
        layer_contents = tile_dict.get(layer_name, [])
        if not isinstance(layer_contents, list):
            # It's not a list if it's e.g. None or _prev_floor, skip
            continue

        for obj in layer_contents:
            info = ALL_SCENERY_DEFS.get(obj.definition_id, {})
            ch_obj = info.get("ascii_char", obj.char)
            obj_color_name = info.get("color_name", "white_on_black")

            # Example: if you want to skip "TreeTop" where the player stands,
            # you can do something like:
            # if obj.definition_id == "TreeTop" and (wx, wy) == (model.player.x, model.player.y):
            #     continue

            # Compose object FG with the floor's BG color
            obj_attr = compose_fg_with_floor_bg(floor_color_name, obj_color_name)
            safe_addch(stdscr, sy, sx, ch_obj, obj_attr, clip_borders=True)


def draw_player_on_top(stdscr, model, map_top_offset):
    """
    Draw the player above everything, but allow certain objects (e.g. TreeTop)
    to render last (so they can obscure the player if desired).
    """
    px = model.player.x - model.camera_x
    py = model.player.y - model.camera_y + map_top_offset
    max_h, max_w = stdscr.getmaxyx()

    if not (0 <= px < max_w and 0 <= py < max_h):
        return  # The player is off-screen

    tile_dict = model.placed_scenery.get((model.player.x, model.player.y), {})
    # Determine the floor color for background merging
    floor_obj = tile_dict.get("floor")
    floor_color_name = "white_on_black"
    if floor_obj:
        fdef = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
        floor_color_name = fdef.get("color_name", "white_on_black")

    # Draw the player using the floor's background color
    player_fg = getattr(model.player, "color_name", "white")  # e.g. "cyan"
    player_char = getattr(model.player, "char", "@")          # e.g. '@'

    player_attr = compose_fg_with_floor_bg(floor_color_name, player_fg)
    safe_addch(stdscr, py, px, player_char, player_attr, clip_borders=True)

    # -------------------------------------------------------
    # LEGACY CODE (commented out) that used layer_for_def_id:
    #
    # objects_list = tile_layers.get(layer_for_def_id, [])
    # trunk_tops = [o for o in objects_list if o.definition_id in (TREE_TRUNK_ID, TREE_TOP_ID)]
    # for t_obj in trunk_tops: ...
    #
    # -------------------------------------------------------

    # If you have certain objects that should obscure the player (like "TreeTop"),
    # gather them from the "objects" or "overhead" layer, etc.:
    trunk_tops = []
    from_layers = get_layers_in_draw_order()
    # We skip "floor" since it doesn't contain lists. But we might check "objects"/"overhead".
    for layer_name in from_layers:
        if layer_name in ("floor",):  
            continue
        maybe_list = tile_dict.get(layer_name, [])
        if isinstance(maybe_list, list):
            for obj in maybe_list:
                if obj.definition_id in ("TreeTop", "TreeTrunk"):
                    trunk_tops.append(obj)

    # Re-draw those trunk/tops last, so they appear over the player
    for t_obj in trunk_tops:
        info = ALL_SCENERY_DEFS.get(t_obj.definition_id, {})
        ch = info.get("ascii_char", t_obj.char)
        top_color = info.get("color_name", "white_on_black")

        trunk_attr = compose_fg_with_floor_bg(floor_color_name, top_color)
        safe_addch(stdscr, py, px, ch, trunk_attr, clip_borders=True)