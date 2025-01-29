# FileName: engine_render.py
# version: 3.4
# Summary: Renders terrain, objects, items, partial updates, and the player in layers.
# Tags: engine, rendering, optimization

import curses
from curses_utils import safe_addch, safe_addstr, get_color_attr, parse_two_color_names
from color_init import color_pairs
from scenery_defs import (
    ALL_SCENERY_DEFS,
    TREE_TRUNK_ID,
    TREE_TOP_ID
)
from scenery_main import (
    FLOOR_LAYER, OBJECTS_LAYER, ITEMS_LAYER, ENTITIES_LAYER
)


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

RENDER_MODE = "ascii"


def _draw_floor(stdscr, floor_obj, sx, sy):
    if floor_obj is None:
        return
    info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
    ch = info.get("ascii_char", floor_obj.char)
    fg_index = info.get("ascii_color", floor_obj.color_pair)

    base_color = LEGACY_COLOR_MAP.get(fg_index, "white_on_black")
    floor_attr = get_color_attr(base_color)
    safe_addch(stdscr, sy, sx, ch, floor_attr, clip_borders=True)


def _draw_object(stdscr, obj, sx, sy, floor_fg_index):
    info = ALL_SCENERY_DEFS.get(obj.definition_id, {})
    ch = info.get("ascii_char", obj.char)
    obj_fg_index = info.get("ascii_color", obj.color_pair)

    # special case: Tree top
    if obj.definition_id == TREE_TOP_ID:
        top_color_name = LEGACY_COLOR_MAP.get(obj_fg_index, "green_on_black")
        top_attr = get_color_attr(top_color_name)
        safe_addch(stdscr, sy, sx, ch, top_attr, clip_borders=True)
        return

    # Normal objects => floor background
    floor_base = LEGACY_COLOR_MAP.get(floor_fg_index, "white_on_black")
    fg_part, bg_part = parse_two_color_names(floor_base)
    obj_color_name = LEGACY_COLOR_MAP.get(obj_fg_index, "white_on_black")
    real_fg, _ = parse_two_color_names(obj_color_name)

    final_color_name = f"{real_fg}_on_{bg_part}"
    obj_attr = get_color_attr(final_color_name)
    safe_addch(stdscr, sy, sx, ch, obj_attr, clip_borders=True)


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
    max_h, max_w = stdscr.getmaxyx()
    player_wx, player_wy = player.x, player.y

    for (wx, wy) in dirty_tiles:
        if not (0 <= wx < world_width and 0 <= wy < world_height):
            continue

        sx = wx - camera_x
        sy = wy - camera_y + map_top_offset
        if sx < 0 or sy < 0 or sx >= max_w or sy >= max_h:
            continue

        blank_attr = get_color_attr("white_on_black")
        safe_addch(stdscr, sy, sx, " ", blank_attr, clip_borders=True)

        tile_layers = placed_scenery.get((wx, wy), None)
        if not tile_layers:
            continue

        # floor
        floor_obj = tile_layers.get(FLOOR_LAYER)
        _draw_floor(stdscr, floor_obj, sx, sy)
        floor_fg_index = 0
        if floor_obj:
            floor_info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
            floor_fg_index = floor_info.get("ascii_color", floor_obj.color_pair)

        # objects
        objects_list = tile_layers.get(OBJECTS_LAYER, [])
        for obj in objects_list:
            if obj.definition_id in (TREE_TRUNK_ID, TREE_TOP_ID):
                if (wx, wy) == (player_wx, player_wy):
                    continue
            _draw_object(stdscr, obj, sx, sy, floor_fg_index)

        # items
        items_list = tile_layers.get(ITEMS_LAYER, [])
        _draw_items(stdscr, items_list, sx, sy, floor_fg_index)

        # entities
        ent_list = tile_layers.get(ENTITIES_LAYER, [])
        _draw_entities(stdscr, ent_list, sx, sy, floor_fg_index)


def draw_layers(stdscr, model):
    px = model.player.x - model.camera_x
    py = model.player.y - model.camera_y + 3
    max_h, max_w = stdscr.getmaxyx()
    if 0 <= px < max_w and 0 <= py < max_h:
        tile_layers = model.placed_scenery.get((model.player.x, model.player.y), None)
        if tile_layers:
            floor_obj = tile_layers.get(FLOOR_LAYER)
            floor_fg_index = 0
            if floor_obj:
                floor_info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
                floor_fg_index = floor_info.get("ascii_color", floor_obj.color_pair)

            floor_base = LEGACY_COLOR_MAP.get(floor_fg_index, "white_on_black")
            fg_part, bg_part = parse_two_color_names(floor_base)
            color_name = f"white_on_{bg_part}"
            player_attr = get_color_attr(color_name, bold=True)
            safe_addch(stdscr, py, px, "@", player_attr, clip_borders=True)

    # trunk/top behind the player
    tile_layers = model.placed_scenery.get((model.player.x, model.player.y), None)
    if tile_layers:
        objects_list = tile_layers.get(OBJECTS_LAYER, [])
        trunk_or_top = [o for o in objects_list if o.definition_id in (TREE_TRUNK_ID, TREE_TOP_ID)]
        if trunk_or_top and 0 <= px < max_w and 0 <= py < max_h:
            for obj in trunk_or_top:
                info = ALL_SCENERY_DEFS.get(obj.definition_id, {})
                ch = info.get("ascii_char", obj.char)
                fg_index = info.get("ascii_color", obj.color_pair)
                base_col = LEGACY_COLOR_MAP.get(fg_index, "white_on_black")
                obj_fg, _ = parse_two_color_names(base_col)
                final_col = f"{obj_fg}_on_white"
                attr = get_color_attr(final_col)
                safe_addch(stdscr, py, px, ch, attr, clip_borders=True)