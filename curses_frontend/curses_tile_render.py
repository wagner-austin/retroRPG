# FileName: curses_tile_render.py
# version: 1.0
#
# Summary:
#   Contains common tile-drawing logic for the curses UI. Moved here from
#   curses_renderer.py to allow a cleaner separation of responsibilities.
#
# Tags: curses, ui, rendering

#import curses
from .curses_utils import safe_addch, parse_two_color_names
from .curses_selector_highlight import get_color_attr
from scenery_defs import ALL_SCENERY_DEFS, TREE_TRUNK_ID, TREE_TOP_ID
from layer_defs import FLOOR_LAYER, OBJECTS_LAYER, ITEMS_LAYER, ENTITIES_LAYER
#from .where_curses_themes_lives import CURRENT_THEME

def draw_single_tile(stdscr, wx, wy, sx, sy, model, blank_attr):
    """
    Draw the background/floor plus any objects, items, or entities for tile (wx, wy).
    Painted at screen coords (sx, sy). The player is NOT drawn here; that is handled
    separately to ensure the player remains above (or below) certain objects.
    """

    # Erase any leftover character first
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

        # Combine floor BG and object FG to preserve the floor background color
        fg_floor, bg_floor = parse_two_color_names(floor_color_name)
        fg_obj, _ = parse_two_color_names(obj_color_name)
        final_color = f"{fg_obj}_on_{bg_floor}"
        attr = get_color_attr(final_color)

        safe_addch(stdscr, sy, sx, ch, attr, clip_borders=True)


def draw_player_on_top(stdscr, model, map_top_offset):
    """
    Draw the player above everything, but below the tree top if it shares the same tile.
    Then, if there's a tree trunk or tree top in the same tile, it goes on top of the player.

    If you'd prefer the player to be truly on top, you can remove the trunk_tops pass below.
    Or if you want a dedicated "player layer," you'd handle that in your layering code
    instead of doing a manual approach here.
    """
    px = model.player.x - model.camera_x
    py = model.player.y - model.camera_y + map_top_offset
    max_h, max_w = stdscr.getmaxyx()

    if 0 <= px < max_w and 0 <= py < max_h:
        tile_layers = model.placed_scenery.get((model.player.x, model.player.y), {})

        # Figure out the floor color for the background
        floor_obj = tile_layers.get(FLOOR_LAYER)
        floor_color_name = "white_on_black"
        if floor_obj:
            finfo = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
            floor_color_name = finfo.get("color_name", "white_on_black")

        # Draw player with the floor-based background but the player's chosen foreground
        fg_floor, bg_floor = parse_two_color_names(floor_color_name)

        # The player's foreground color and character come only from player_char.py
        player_fg = getattr(model.player, "color_name", "white")  # default to 'white' if not set
        player_char = getattr(model.player, "char", "@")          # default to '@' if not set

        player_color = f"{player_fg}_on_{bg_floor}"
        attr_bold = get_color_attr(player_color, bold=True)
        safe_addch(stdscr, py, px, player_char, attr_bold, clip_borders=True)

        # If there's a trunk/top in the same tile, it goes on top of the player
        objects_list = tile_layers.get(OBJECTS_LAYER, [])
        trunk_tops = [o for o in objects_list if o.definition_id in (TREE_TRUNK_ID, TREE_TOP_ID)]
        for t_obj in trunk_tops:
            info = ALL_SCENERY_DEFS.get(t_obj.definition_id, {})
            ch = info.get("ascii_char", t_obj.char)
            top_color = info.get("color_name", "white_on_black")

            fg_obj, _ = parse_two_color_names(top_color)
            final_color = f"{fg_obj}_on_{bg_floor}"
            trunk_attr = get_color_attr(final_color)
            safe_addch(stdscr, py, px, ch, trunk_attr, clip_borders=True)