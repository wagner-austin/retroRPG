# FileName: scenery_placement_utils.py
# version: 1.0
# Summary: Provides shared functions for placing scenery items (tree, bridge, etc.) 
#          used by both scenery_floor_main.py and scenery_objects_main.py.
# Tags: scenery, placement, utils

from scenery_defs import (
    RIVER_ID, TREE_ID, TREE_TRUNK_ID, TREE_TOP_ID,
    BRIDGE_ID, BRIDGE_END_ID, BRIDGE_TOOL_ID
)
from scenery_core import (
    SceneryObject,
    get_objects_at,
    remove_scenery,
    append_scenery
)

def place_tree(player, placed_scenery, mark_dirty_func):
    """
    Places a tree trunk at (player.x, player.y) plus a tree top one tile above, if available.
    """
    px, py = player.x, player.y
    trunk_obj = SceneryObject(px, py, TREE_TRUNK_ID)
    append_scenery(placed_scenery, trunk_obj)
    mark_dirty_func(px, py)

    top_obj = None
    if py > 0:
        top_obj = SceneryObject(px, py - 1, TREE_TOP_ID)
        append_scenery(placed_scenery, top_obj)
        mark_dirty_func(px, py - 1)

    return trunk_obj, top_obj


def place_bridge_across_river(player, placed_scenery, mark_dirty_func,
                              world_width=100, world_height=60, is_editor=False):
    """
    Creates a continuous bridge across any contiguous line of RIVER floor tiles.
    Overwrites old BRIDGE_END objects, then places new Bridge tiles plus 'bridge ends.'
    """
    dx = dy = 0
    if player.last_move_direction == "up":
        dy = -1
    elif player.last_move_direction == "down":
        dy = 1
    elif player.last_move_direction == "left":
        dx = -1
    elif player.last_move_direction == "right":
        dx = 1

    cx = player.x + dx
    cy = player.y + dy

    water_tiles = []
    while True:
        tile_objs = get_objects_at(placed_scenery, cx, cy)
        found_river = next((o for o in tile_objs if o.definition_id == RIVER_ID), None)
        if not found_river:
            break
        water_tiles.append(found_river)
        cx += dx
        cy += dy

    if not water_tiles:
        return []

    newly_placed = []
    for wobj in water_tiles:
        # Remove old BRIDGE_END from the same tile
        tile_objs2 = get_objects_at(placed_scenery, wobj.x, wobj.y)
        ends = [o for o in tile_objs2 if o.definition_id == BRIDGE_END_ID]
        for e in ends:
            remove_scenery(placed_scenery, e)

        new_bridge = SceneryObject(wobj.x, wobj.y, BRIDGE_ID)
        append_scenery(placed_scenery, new_bridge)
        mark_dirty_func(wobj.x, wobj.y)
        newly_placed.append(new_bridge)

    # Place "bridge ends" at the edges
    start_x = water_tiles[0].x - dx
    start_y = water_tiles[0].y - dy
    end_x   = water_tiles[-1].x + dx
    end_y   = water_tiles[-1].y + dy

    for (ex, ey) in [(start_x, start_y), (end_x, end_y)]:
        tile_objs3 = get_objects_at(placed_scenery, ex, ey)
        has_bridge = any(o.definition_id == BRIDGE_ID for o in tile_objs3)
        is_river   = any(o.definition_id == RIVER_ID  for o in tile_objs3)
        if not has_bridge and not is_river:
            bend = SceneryObject(ex, ey, BRIDGE_END_ID)
            append_scenery(placed_scenery, bend)
            mark_dirty_func(ex, ey)
            newly_placed.append(bend)

    return newly_placed


def place_scenery_item(def_id, player, placed_scenery, mark_dirty_func,
                       is_editor=False, world_width=100, world_height=60):
    """
    Places a scenery item (e.g. tree trunk, bridging across river).
    If def_id == BRIDGE_TOOL_ID and is_editor, triggers a multi-tile bridging.
    If def_id == TREE_ID and is_editor, places trunk + top.
    Otherwise, just places one object at player's location.
    """
    newly_placed = []

    if def_id == BRIDGE_TOOL_ID and is_editor:
        new_objs = place_bridge_across_river(
            player, placed_scenery, mark_dirty_func,
            world_width=world_width,
            world_height=world_height,
            is_editor=True
        )
        newly_placed.extend(new_objs)
    elif def_id == TREE_ID and is_editor:
        trunk_obj, top_obj = place_tree(player, placed_scenery, mark_dirty_func)
        newly_placed.append(trunk_obj)
        if top_obj:
            newly_placed.append(top_obj)
    else:
        obj = SceneryObject(player.x, player.y, def_id)
        append_scenery(placed_scenery, obj)
        mark_dirty_func(player.x, player.y)
        newly_placed.append(obj)

    return newly_placed
