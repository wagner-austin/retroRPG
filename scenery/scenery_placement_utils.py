# FileName: scenery_placement_utils.py
# version: 1.1 (refactored)
# Summary: Provides shared functions for placing scenery items (tree, bridge, etc.)
# Tags: scenery, placement, utils

#from scenery_data.scenery_manager import ALL_SCENERY_DEFS  # if you want to reference tile data

from scenery.scenery_core import (
    SceneryObject,
    get_objects_at,
    remove_scenery,
    append_scenery
)

# -------------------------------------------------------------------------
# 1) Define tile IDs for logic here (previously imported from scenery_defs).
#    You can rename or move these if you prefer a different organization.
# -------------------------------------------------------------------------
RIVER_ID        = "River"
TREE_ID         = "Tree"
TREE_TRUNK_ID   = "TreeTrunk"
TREE_TOP_ID     = "TreeTop"
BRIDGE_ID       = "Bridge"
BRIDGE_END_ID   = "BridgeEnd"
BRIDGE_TOOL_ID  = "BridgeTool"

def place_tree(player, placed_scenery, mark_dirty_func):
    """
    Places a tree trunk at (player.x, player.y) plus a tree top one tile above (if valid).
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

    # Figure out which direction the player is facing.
    dx = dy = 0
    if player.last_move_direction == "up":
        dy = -1
    elif player.last_move_direction == "down":
        dy = 1
    elif player.last_move_direction == "left":
        dx = -1
    elif player.last_move_direction == "right":
        dx = 1

    # Walk outward from player's position, collecting consecutive "River" tiles.
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

    # If no river tiles found, do nothing.
    if not water_tiles:
        return []

    newly_placed = []
    # For each river tile, remove any old bridge ends and place a Bridge tile.
    for wobj in water_tiles:
        tile_objs2 = get_objects_at(placed_scenery, wobj.x, wobj.y)
        ends = [o for o in tile_objs2 if o.definition_id == BRIDGE_END_ID]
        for e in ends:
            remove_scenery(placed_scenery, e)

        new_bridge = SceneryObject(wobj.x, wobj.y, BRIDGE_ID)
        append_scenery(placed_scenery, new_bridge)
        mark_dirty_func(wobj.x, wobj.y)
        newly_placed.append(new_bridge)

    # Place "bridge ends" just outside the river on both sides.
    start_x = water_tiles[0].x - dx
    start_y = water_tiles[0].y - dy
    end_x   = water_tiles[-1].x + dx
    end_y   = water_tiles[-1].y + dy

    for (ex, ey) in [(start_x, start_y), (end_x, end_y)]:
        tile_objs3 = get_objects_at(placed_scenery, ex, ey)
        has_bridge = any(o.definition_id == BRIDGE_ID for o in tile_objs3)
        is_river   = any(o.definition_id == RIVER_ID for o in tile_objs3)
        # Only place a bridge end if there's no bridge and no river here.
        if not has_bridge and not is_river:
            bend = SceneryObject(ex, ey, BRIDGE_END_ID)
            append_scenery(placed_scenery, bend)
            mark_dirty_func(ex, ey)
            newly_placed.append(bend)

    return newly_placed

def place_scenery_item(def_id, player, placed_scenery, mark_dirty_func,
                       is_editor=False, world_width=100, world_height=60):
    """
    Places a scenery item (e.g., a tree trunk, bridging across a river).
    If def_id == BRIDGE_TOOL_ID and is_editor, triggers multi-tile bridging (place_bridge_across_river).
    If def_id == TREE_ID and is_editor, places trunk + top (place_tree).
    Otherwise, just places one object at the player's location.
    """
    newly_placed = []

    # If the user is in the editor and the def_id is the bridge tool, do bridging logic:
    if def_id == BRIDGE_TOOL_ID and is_editor:
        new_objs = place_bridge_across_river(
            player, placed_scenery, mark_dirty_func,
            world_width=world_width,
            world_height=world_height,
            is_editor=True
        )
        newly_placed.extend(new_objs)

    # If the user is in the editor and the def_id is a "Tree", place a trunk + top:
    elif def_id == TREE_ID and is_editor:
        trunk_obj, top_obj = place_tree(player, placed_scenery, mark_dirty_func)
        newly_placed.append(trunk_obj)
        if top_obj:
            newly_placed.append(top_obj)

    # Otherwise, just place one object:
    else:
        obj = SceneryObject(player.x, player.y, def_id)
        append_scenery(placed_scenery, obj)
        mark_dirty_func(player.x, player.y)
        newly_placed.append(obj)

    return newly_placed