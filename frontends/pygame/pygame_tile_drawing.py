# File: pygame_tile_drawing.py
# version: 1.2 (refactored to remove layer_for_def_id usage in rendering)
#
# Summary:
#   Contains common tile-drawing logic for the pygame UI. Moved here from
#   the renderer to allow a cleaner separation of responsibilities.
#
# ChangeLog:
#   v1.1:  - Added `compose_fg_with_floor_bg` helper to remove repeated code.
#          - Updated `draw_single_tile` & `draw_player_on_top` to use helper.
#   v1.2:  - Now draws floor plus other layers from layer_manager.get_layers_in_draw_order().
#          - The old code referencing layer_for_def_id is commented out.
#
# Tags: pygame, ui, rendering

from .pygame_utils import safe_addch, parse_two_color_names
from .pygame_selector_highlight import get_color_attr

# We still need ALL_SCENERY_DEFS for character and color lookups.
from scenery.scenery_manager import ALL_SCENERY_DEFS

# Import the layer order helper so we can draw in ascending z-index.
from scenery.layer_manager import get_layers_in_draw_order

def compose_fg_with_floor_bg(floor_color_name, fg_object_color_name):
    """
    Given a floor color name (e.g. "white_on_black") and an object's
    foreground color name (e.g. "red_on_black"), combine them so that:
      - The object's foreground remains the same,
      - The background becomes whatever the floor's background was.
    Returns a pygame color attribute (an RGB tuple).
    """
    fg_floor, bg_floor = parse_two_color_names(floor_color_name)
    fg_obj, _ = parse_two_color_names(fg_object_color_name)
    final_color_name = f"{fg_obj}_on_{bg_floor}"
    return get_color_attr(final_color_name)

def draw_single_tile(screen, wx, wy, sx, sy, model, blank_attr):
    """
    Draw the background/floor plus any objects, items, or entities for tile (wx, wy).
    Painted at screen coordinates (sx, sy). The player is NOT drawn here; that is handled
    separately to ensure the player remains above (or below) certain objects.
    """

    # Erase any leftover character first.
    safe_addch(screen, sy, sx, " ", blank_attr, clip_borders=True)

    tile_dict = model.placed_scenery.get((wx, wy), None)
    if not tile_dict:
        return  # nothing to draw

    # NEW: multi-layer drawing approach
    # 1) Draw the floor first.
    floor_obj = tile_dict.get("floor")
    floor_color_name = "white_on_black"

    if floor_obj:
        fdef = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
        ch_floor = fdef.get("ascii_char", floor_obj.char)
        floor_color_name = fdef.get("color_name", "white_on_black")
        floor_attr = get_color_attr(floor_color_name)
        safe_addch(screen, sy, sx, ch_floor, floor_attr, clip_borders=True)

    # 2) Draw every other layer in ascending z‐order,
    #    skipping "floor" because we already drew it above.
    layers_in_order = get_layers_in_draw_order()
    for layer_name in layers_in_order:
        if layer_name == "floor":
            continue  # already handled

        # tile_dict might have, for example, tile_dict["objects"] = [...]
        layer_contents = tile_dict.get(layer_name, [])
        if not isinstance(layer_contents, list):
            # It's not a list (e.g. None or some legacy value); skip it.
            continue

        for obj in layer_contents:
            info = ALL_SCENERY_DEFS.get(obj.definition_id, {})
            ch_obj = info.get("ascii_char", obj.char)
            obj_color_name = info.get("color_name", "white_on_black")

            # Compose the object's foreground with the floor's background.
            obj_attr = compose_fg_with_floor_bg(floor_color_name, obj_color_name)
            safe_addch(screen, sy, sx, ch_obj, obj_attr, clip_borders=True)

def draw_player_on_top(screen, model, map_top_offset):
    """
    Draw the player above everything, but allow certain objects (e.g. TreeTop)
    to render last (so they can obscure the player if desired).
    """
    px = model.player.x - model.camera_x
    py = model.player.y - model.camera_y + map_top_offset
    width, height = screen.get_size()

    if not (0 <= px < width and 0 <= py < height):
        return  # The player is off-screen

    tile_dict = model.placed_scenery.get((model.player.x, model.player.y), {})
    # Determine the floor color for background merging.
    floor_obj = tile_dict.get("floor")
    floor_color_name = "white_on_black"
    if floor_obj:
        fdef = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
        floor_color_name = fdef.get("color_name", "white_on_black")

    # Draw the player using the floor's background color.
    player_fg = getattr(model.player, "color_name", "white")  # e.g. "cyan"
    player_char = getattr(model.player, "char", "@")           # e.g. '@'

    player_attr = compose_fg_with_floor_bg(floor_color_name, player_fg)
    safe_addch(screen, py, px, player_char, player_attr, clip_borders=True)

    # If you have certain objects that should obscure the player (like "TreeTop"),
    # gather them from the "objects" or "overhead" layer.
    trunk_tops = []
    from_layers = get_layers_in_draw_order()
    # Skip "floor" since it doesn't contain lists. Check other layers such as "objects" or "overhead".
    for layer_name in from_layers:
        if layer_name == "floor":
            continue
        maybe_list = tile_dict.get(layer_name, [])
        if isinstance(maybe_list, list):
            for obj in maybe_list:
                if obj.definition_id in ("TreeTop", "TreeTrunk"):
                    trunk_tops.append(obj)

    # Re-draw those trunk/tops last, so they appear over the player.
    for t_obj in trunk_tops:
        info = ALL_SCENERY_DEFS.get(t_obj.definition_id, {})
        ch = info.get("ascii_char", t_obj.char)
        top_color = info.get("color_name", "white_on_black")
        trunk_attr = compose_fg_with_floor_bg(floor_color_name, top_color)
        safe_addch(screen, py, px, ch, trunk_attr, clip_borders=True)
