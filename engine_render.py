# FileName: engine_render.py
# version: 3.2
# Summary: Renders terrain, objects, items, partial updates, and the player in layers.
#          - "floor" -> "objects" -> "items" -> then player
#          - If a tree trunk or top is on the player's tile, it is drawn last with a white background.
# Tags: engine, rendering, optimization

import curses
from color_init import color_pairs
from scenery_defs import (
    ALL_SCENERY_DEFS,
    TREE_TRUNK_ID,
    TREE_TOP_ID
)
from scenery_main import (
    FLOOR_TYPE_IDS,
    FLOOR_LAYER, OBJECTS_LAYER, ITEMS_LAYER, ENTITIES_LAYER
)


##############################################################################
# PART 1: Legacy color map for ASCII usage
##############################################################################
LEGACY_COLOR_MAP = {
    1:  "green_on_black",
    2:  "yellow_on_black",
    3:  "white_on_black",
    4:  "white_on_blue",
    5:  "white_on_green",
    7:  "green_on_white",
    8:  "black_on_yellow",
    12: "yellow_on_black",
    16: "white_on_black",
    17: "red_on_black",
    # etc.
}

##############################################################################
# PART 2: LAYERED RENDER
##############################################################################
RENDER_MODE = "ascii"


def _build_color_attr(fg_index, bg_name):
    """
    Given a numeric 'ascii_color' or 'color_pair' for the foreground,
    and a string color name for the background (e.g. "black", "blue", "green"),
    create a curses attribute that merges them.
    """
    # Look up the base color name
    base_color = LEGACY_COLOR_MAP.get(fg_index, "white_on_black")
    splitted = base_color.split("_on_")
    if len(splitted) == 2:
        fg_part, _ = splitted
    else:
        fg_part = "white"

    # final "fg_part_on_bg_name"
    final_name = f"{fg_part}_on_{bg_name}"
    pair_id = color_pairs.get(final_name, 0)
    return curses.color_pair(pair_id)


def _render_one_ascii(stdscr, x_screen, y_screen, ascii_char, attr):
    """
    Safely render a single character with the given curses attribute at (y_screen, x_screen).
    """
    max_h, max_w = stdscr.getmaxyx()
    if 0 <= x_screen < max_w and 0 <= y_screen < max_h:
        try:
            stdscr.addch(y_screen, x_screen, ascii_char, attr)
        except curses.error:
            pass


def _draw_floor(stdscr, floor_obj, sx, sy):
    if floor_obj is None:
        return
    info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
    ch = info.get("ascii_char", floor_obj.char)
    fg_index = info.get("ascii_color", floor_obj.color_pair)

    # The floor uses its own background color (from legacy_color_map).
    base_color = LEGACY_COLOR_MAP.get(fg_index, "white_on_black")
    pair_id = color_pairs.get(base_color, 0)
    attr = curses.color_pair(pair_id)

    _render_one_ascii(stdscr, sx, sy, ch, attr)


def _draw_object(stdscr, obj, sx, sy, floor_fg_index):
    """
    Draw a single object with:
      - object’s foreground color
      - the floor’s background color
    Except for TREE_TOP_ID, which always uses green_on_black so it doesn't vanish on grass.
    """
    info = ALL_SCENERY_DEFS.get(obj.definition_id, {})
    ch = info.get("ascii_char", obj.char)
    obj_fg_index = info.get("ascii_color", obj.color_pair)

    # Special case: Tree top always green_on_black, ignoring floor
    if obj.definition_id == TREE_TOP_ID:
        top_color_name = LEGACY_COLOR_MAP.get(obj_fg_index, "green_on_black")  
        pair_id = color_pairs.get(top_color_name, 0)
        attr = curses.color_pair(pair_id)
        _render_one_ascii(stdscr, sx, sy, ch, attr)
        return

    # Normal objects => use the floor's background
    floor_base = LEGACY_COLOR_MAP.get(floor_fg_index, "white_on_black")
    parts = floor_base.split("_on_")
    if len(parts) == 2:
        floor_bg = parts[1]
    else:
        floor_bg = "black"

    attr = _build_color_attr(obj_fg_index, floor_bg)
    _render_one_ascii(stdscr, sx, sy, ch, attr)


def _draw_items(stdscr, items_list, sx, sy, floor_fg_index):
    for it in items_list:
        _draw_object(stdscr, it, sx, sy, floor_fg_index)


def _draw_entities(stdscr, entities_list, sx, sy, floor_fg_index):
    for ent in entities_list:
        _draw_object(stdscr, ent, sx, sy, floor_fg_index)


def mark_dirty(model, x, y):
    model.dirty_tiles.add((x, y))


def update_partial_tiles_in_view(
    stdscr,
    player,
    placed_scenery,
    camera_x,
    camera_y,
    map_top_offset,
    dirty_tiles,
    action_flash_info=None,
    world_width=100,
    world_height=60
):
    """
    Only re-draw the (x,y) in dirty_tiles, by layering approach:
      floor -> objects -> items -> entities
    We'll skip drawing tree trunk/tops if the player is on that tile,
    so we can handle them specially after the player is drawn.
    """
    max_h, max_w = stdscr.getmaxyx()
    player_wx, player_wy = player.x, player.y

    for (wx, wy) in dirty_tiles:
        if not (0 <= wx < world_width and 0 <= wy < world_height):
            continue

        sx = wx - camera_x
        sy = wy - camera_y + map_top_offset
        if sx < 0 or sy < 0 or sx >= max_w or sy >= max_h:
            continue

        # Clear/blank first
        blank_attr = curses.color_pair(color_pairs.get("white_on_black", 0))
        try:
            stdscr.addch(sy, sx, " ", blank_attr)
        except curses.error:
            pass

        tile_layers = placed_scenery.get((wx, wy), None)
        if not tile_layers:
            # No tile => black
            continue

        # 1) draw floor
        floor_obj = tile_layers.get(FLOOR_LAYER)
        _draw_floor(stdscr, floor_obj, sx, sy)

        # We need floor's ascii_color to pass as "background" to objects/items
        floor_info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {}) if floor_obj else {}
        floor_fg_index = floor_info.get("ascii_color", floor_obj.color_pair if floor_obj else 0)

        # 2) draw objects (except trunk/top if player is here)
        objects_list = tile_layers.get(OBJECTS_LAYER, [])
        for obj in objects_list:
            if obj.definition_id in (TREE_TRUNK_ID, TREE_TOP_ID):
                # If the player is on the same tile, we skip for now
                # so we can handle it in draw_layers (which draws it last).
                if (wx, wy) == (player_wx, player_wy):
                    continue
            _draw_object(stdscr, obj, sx, sy, floor_fg_index)

        # 3) draw items
        items_list = tile_layers.get(ITEMS_LAYER, [])
        _draw_items(stdscr, items_list, sx, sy, floor_fg_index)

        # 4) draw entities
        ent_list = tile_layers.get(ENTITIES_LAYER, [])
        _draw_entities(stdscr, ent_list, sx, sy, floor_fg_index)

        # action flash, if any, can be drawn here if you want
        # (omitted for brevity)


def draw_layers(stdscr, model):
    """
    After partial updates. The player is drawn (normally) last, so it appears
    above objects – except for tree trunk/tops if the user is on that tile,
    which we specifically draw after the player to simulate "behind the tree."

    The player's background always uses the floor tile's background color,
    ignoring objects on that tile (like a bridge post).
    """
    # 1) Draw the player normally
    px = model.player.x - model.camera_x
    py = model.player.y - model.camera_y + 3
    max_h, max_w = stdscr.getmaxyx()
    if 0 <= px < max_w and 0 <= py < max_h:
        tile_layers = model.placed_scenery.get((model.player.x, model.player.y), None)
        if tile_layers:
            floor_obj = tile_layers.get(FLOOR_LAYER)
            if floor_obj:
                floor_info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
                floor_fg_index = floor_info.get("ascii_color", floor_obj.color_pair)
            else:
                floor_fg_index = 0

            # build "white_on_<floor_bg>" for the player's color
            floor_base = LEGACY_COLOR_MAP.get(floor_fg_index, "white_on_black")
            parts = floor_base.split("_on_")
            if len(parts) == 2:
                floor_bg = parts[1]
            else:
                floor_bg = "black"

            # The player's foreground is white, background = floor_bg
            color_name = f"white_on_{floor_bg}"
            pair_id = color_pairs.get(color_name, 0)
            attr = curses.color_pair(pair_id) | curses.A_BOLD

            # Draw the player '@'
            try:
                stdscr.addch(py, px, "@", attr)
            except curses.error:
                pass

    # 2) If there's a tree trunk or top in the player's tile, draw it on top with white background
    #    to simulate the player being "behind" the tree.
    tile_layers = model.placed_scenery.get((model.player.x, model.player.y), None)
    if tile_layers:
        objects_list = tile_layers.get(OBJECTS_LAYER, [])
        trunk_or_top = [obj for obj in objects_list if obj.definition_id in (TREE_TRUNK_ID, TREE_TOP_ID)]
        if trunk_or_top:
            # We forcibly draw them again, using a white background
            for obj in trunk_or_top:
                obj_info = ALL_SCENERY_DEFS.get(obj.definition_id, {})
                ch = obj_info.get("ascii_char", obj.char)
                fg_index = obj_info.get("ascii_color", obj.color_pair)

                # We want to keep the original object's foreground but place background = white
                base_color = LEGACY_COLOR_MAP.get(fg_index, "white_on_black")
                parts = base_color.split("_on_")
                if len(parts) == 2:
                    obj_fg = parts[0]
                else:
                    obj_fg = "white"
                final_color = f"{obj_fg}_on_white"
                pair_id = color_pairs.get(final_color, 0)
                attr = curses.color_pair(pair_id)
                try:
                    stdscr.addch(py, px, ch, attr)
                except curses.error:
                    pass