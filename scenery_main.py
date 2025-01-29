# FileName: scenery_main.py
# version: 3.6 (renamed functions, moved ensure_layered_format)
# Summary: Manages all scenery objects (trees, rocks, bridges), ensuring "floor" tiles
#          (grass, river, path, etc.) are placed at the bottom of the stack.
#          Also ensures robust handling of '_prev_floor' in legacy or partially-initialized tiles.
# Tags: scenery, map, collision

from scenery_defs import (
    ALL_SCENERY_DEFS,
    build_forward_map,
    build_reverse_map,
    TREE_TRUNK_ID,
    TREE_TOP_ID,
    ROCK_ID,
    BRIDGE_ID,
    BRIDGE_END_ID,
    RIVER_ID,
    GRASS_ID,
    PATH_ID,
    TREE_ID,
    BRIDGE_TOOL_ID,
    SEMICOLON_FLOOR_ID,
    EMPTY_FLOOR_ID,
    DEBUG_DOT_ID
)

##############################################################################
# 0) LAYER CONSTANTS
##############################################################################
FLOOR_LAYER   = "floor"    
OBJECTS_LAYER = "objects"  
ITEMS_LAYER   = "items"    
ENTITIES_LAYER= "entities" 

# All "floor" type IDs => stored in the 'floor' layer
FLOOR_TYPE_IDS = {
    RIVER_ID,
    GRASS_ID,
    PATH_ID,
    SEMICOLON_FLOOR_ID,
    EMPTY_FLOOR_ID
}

# Some "object" type IDs => stored in the 'objects' layer
OBJECT_TYPE_IDS = {
    ROCK_ID,
    TREE_TRUNK_ID,
    TREE_TOP_ID,
    BRIDGE_ID,
    BRIDGE_END_ID,
    BRIDGE_TOOL_ID,
}

# If you eventually define item IDs in scenery_defs, put them in ITEM_TYPE_IDS
ITEM_TYPE_IDS = set()

# If you want to store monsters/NPCs in scenery, define them in ENTITIES_TYPE_IDS
ENTITIES_TYPE_IDS = set()

##############################################################################
# REGISTERING / GET-PLACEABLE DEFS
##############################################################################
def register_scenery(definition_id, char, color_pair, blocking, placeable):
    ALL_SCENERY_DEFS[definition_id] = {
        "char": char,
        "color_pair": color_pair,
        "blocking": blocking,
        "placeable": placeable
    }

def get_placeable_scenery_defs():
    return [
        def_id
        for def_id, info in ALL_SCENERY_DEFS.items()
        if info.get("placeable", False)
    ]


##############################################################################
# SCENERYOBJECT
##############################################################################
class SceneryObject:
    """
    Basic container for definition_id, char, color_pair, x, y.
    """
    def __init__(self, x, y, paramA, paramB=None):
        self.x = x
        self.y = y
        self.definition_id = None
        self.char = "?"
        self.color_pair = 0

        # Use static caching to avoid rebuilding maps repeatedly.
        if not hasattr(self.__class__, "_forward_cache"):
            self.__class__._forward_cache = build_forward_map()
            self.__class__._reverse_cache = build_reverse_map()

        forward_map = self.__class__._forward_cache
        reverse_map = self.__class__._reverse_cache

        if paramB is None:
            # paramA = def_id
            def_id = paramA
            self.definition_id = def_id
            char_col = forward_map.get(def_id, ("?", 0))
            self.char = char_col[0]
            self.color_pair = char_col[1]
        else:
            # paramA = char, paramB = color
            c = paramA
            col = paramB
            self.char = c
            self.color_pair = col
            self.definition_id = reverse_map.get((c, col), None)


##############################################################################
# LAYER-BASED DICTIONARY & HELPER FUNCTIONS
##############################################################################

def ensure_layered_format(placed_scenery):
    """
    Ensures that placed_scenery[(x,y)] is a dictionary with keys:
      'floor', 'objects', 'items', 'entities', '_prev_floor'
    rather than just a list of SceneryObjects or None.

    Converts old-style data into the new layered structure in-place.
    """
    if not placed_scenery:
        return placed_scenery  # Nothing to convert

    # Peek at one tile to see if it's already a dict with 'floor' etc.
    first_key = next(iter(placed_scenery))
    first_val = placed_scenery[first_key]

    if isinstance(first_val, dict) and FLOOR_LAYER in first_val:
        # It's already in layered form
        return placed_scenery

    # Otherwise, convert from list-of-objects => layered dict
    new_dict = {}
    for (x, y), obj_list in placed_scenery.items():
        tile_dict = {
            FLOOR_LAYER: None,
            OBJECTS_LAYER: [],
            ITEMS_LAYER: [],
            ENTITIES_LAYER: [],
            '_prev_floor': None
        }
        for obj in obj_list:
            layer_name = layer_for_def_id(obj.definition_id)
            if layer_name == FLOOR_LAYER:
                tile_dict[FLOOR_LAYER] = obj
            else:
                tile_dict[layer_name].append(obj)
        new_dict[(x, y)] = tile_dict

    return new_dict

def layer_for_def_id(def_id):
    """
    Decide which layer to place a definition_id into.
    If unknown, default to 'objects' so it remains visible.
    """
    if def_id in FLOOR_TYPE_IDS:
        return FLOOR_LAYER
    elif def_id in OBJECT_TYPE_IDS:
        return OBJECTS_LAYER
    elif def_id in ITEM_TYPE_IDS:
        return ITEMS_LAYER
    elif def_id in ENTITIES_TYPE_IDS:
        return ENTITIES_LAYER
    else:
        return OBJECTS_LAYER

def _init_tile_layers(placed_scenery, x, y):
    """
    Ensures placed_scenery[(x,y)] has the full dict. 
    (Helper for append_scenery/remove_scenery/etc.)
    """
    if (x,y) not in placed_scenery:
        placed_scenery[(x,y)] = {
            FLOOR_LAYER:   None,
            OBJECTS_LAYER: [],
            ITEMS_LAYER:   [],
            ENTITIES_LAYER: [],
            '_prev_floor': None
        }
    else:
        tile_layers = placed_scenery[(x,y)]
        if FLOOR_LAYER not in tile_layers:
            tile_layers[FLOOR_LAYER] = None
        if OBJECTS_LAYER not in tile_layers:
            tile_layers[OBJECTS_LAYER] = []
        if ITEMS_LAYER not in tile_layers:
            tile_layers[ITEMS_LAYER] = []
        if ENTITIES_LAYER not in tile_layers:
            tile_layers[ENTITIES_LAYER] = []
        if '_prev_floor' not in tile_layers:
            tile_layers['_prev_floor'] = None


def append_scenery(placed_scenery, obj):
    """
    Places 'obj' into the correct layer at (obj.x, obj.y).
    - If floor => overwrites the old floor (storing it in '_prev_floor')
    - If object => appends in objects layer
    - If item => appends in the items layer
    - If entity => appends in the entities layer
    If there's no floor present, we default to EMPTY_FLOOR.
    """
    x, y = obj.x, obj.y
    _init_tile_layers(placed_scenery, x, y)

    tile_layers = placed_scenery[(x,y)]
    layer_name = layer_for_def_id(obj.definition_id)

    if layer_name == FLOOR_LAYER:
        if tile_layers[FLOOR_LAYER] and tile_layers[FLOOR_LAYER].definition_id != obj.definition_id:
            tile_layers['_prev_floor'] = tile_layers[FLOOR_LAYER]
        tile_layers[FLOOR_LAYER] = obj
    else:
        if tile_layers[FLOOR_LAYER] is None:
            tile_layers[FLOOR_LAYER] = SceneryObject(x, y, EMPTY_FLOOR_ID)
        tile_layers[layer_name].append(obj)


def remove_scenery(placed_scenery, obj):
    """
    Removes 'obj' from whichever layer it belongs to.
    If removing a floor object:
      - If '_prev_floor' is not None, revert to that old floor
      - Otherwise, set floor to None
    Then if everything is empty/no floor, we set floor to EMPTY_FLOOR.
    """
    x, y = obj.x, obj.y
    if (x,y) not in placed_scenery:
        return

    tile_layers = placed_scenery[(x,y)]
    if '_prev_floor' not in tile_layers:
        tile_layers['_prev_floor'] = None

    layer_name = layer_for_def_id(obj.definition_id)

    if layer_name == FLOOR_LAYER:
        if tile_layers[FLOOR_LAYER] == obj:
            if tile_layers['_prev_floor'] is not None:
                tile_layers[FLOOR_LAYER] = tile_layers['_prev_floor']
                tile_layers['_prev_floor'] = None
            else:
                tile_layers[FLOOR_LAYER] = None
    elif layer_name == OBJECTS_LAYER:
        if obj in tile_layers[OBJECTS_LAYER]:
            tile_layers[OBJECTS_LAYER].remove(obj)
    elif layer_name == ITEMS_LAYER:
        if obj in tile_layers[ITEMS_LAYER]:
            tile_layers[ITEMS_LAYER].remove(obj)
    elif layer_name == ENTITIES_LAYER:
        if obj in tile_layers[ENTITIES_LAYER]:
            tile_layers[ENTITIES_LAYER].remove(obj)

    # If everything else is empty/no floor, set a default floor
    if (tile_layers[FLOOR_LAYER] is None and
        not tile_layers[OBJECTS_LAYER] and
        not tile_layers[ITEMS_LAYER] and
        not tile_layers[ENTITIES_LAYER]):
        tile_layers[FLOOR_LAYER] = SceneryObject(x, y, EMPTY_FLOOR_ID)
        tile_layers['_prev_floor'] = None


def get_objects_at(placed_scenery, x, y):
    """
    Merges floor + objects + items + entities into a single list from bottom -> top.
    floor (if any) -> objects -> items -> entities
    """
    if (x,y) not in placed_scenery:
        return []
    tile_layers = placed_scenery[(x,y)]
    merged = []
    if tile_layers[FLOOR_LAYER]:
        merged.append(tile_layers[FLOOR_LAYER])
    merged.extend(tile_layers[OBJECTS_LAYER])
    merged.extend(tile_layers[ITEMS_LAYER])
    merged.extend(tile_layers[ENTITIES_LAYER])
    return merged

##############################################################################
# COLLISION & LOOKUP LOGIC
##############################################################################
def is_blocked(x, y, placed_scenery):
    merged_stack = get_objects_at(placed_scenery, x, y)
    if not merged_stack:
        return False
    top_obj = merged_stack[-1]
    info = ALL_SCENERY_DEFS.get(top_obj.definition_id, None)
    return (info and info.get("blocking", False))

def get_stacked_objs(x, y, placed_scenery):
    return get_objects_at(placed_scenery, x, y)

def get_topmost_obj(x, y, placed_scenery):
    merged_stack = get_objects_at(placed_scenery, x, y)
    return merged_stack[-1] if merged_stack else None

def get_scenery_def_id_at(x, y, placed_scenery):
    top = get_topmost_obj(x, y, placed_scenery)
    return top.definition_id if top else None

def get_scenery_color_at(x, y, placed_scenery):
    top = get_topmost_obj(x, y, placed_scenery)
    return top.color_pair if top else 0

##############################################################################
# PLACEMENT LOGIC
##############################################################################
def place_scenery_item(def_id, player, placed_scenery, mark_dirty_func,
                       is_editor=False, world_width=100, world_height=60):
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

def place_tree(player, placed_scenery, mark_dirty_func):
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
                              world_width=100, world_height=60,
                              is_editor=False):
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
    while 0 <= cx < world_width and 0 <= cy < world_height:
        tile_objs = get_objects_at(placed_scenery, cx, cy)
        found_river = None
        for obj in tile_objs:
            if obj.definition_id == RIVER_ID:
                found_river = obj
                break
        if not found_river:
            break
        water_tiles.append(found_river)
        cx += dx
        cy += dy

    if not water_tiles:
        return []

    newly_placed = []
    for wobj in water_tiles:
        # Keep the river as the floor, do NOT remove it.
        # Remove any existing BridgeEnd in that same tile.
        tile_objs2 = get_objects_at(placed_scenery, wobj.x, wobj.y)
        endpoints = [o for o in tile_objs2 if o.definition_id == BRIDGE_END_ID]
        for e in endpoints:
            remove_scenery(placed_scenery, e)

        new_bridge = SceneryObject(wobj.x, wobj.y, BRIDGE_ID)
        append_scenery(placed_scenery, new_bridge)
        mark_dirty_func(wobj.x, wobj.y)
        newly_placed.append(new_bridge)

    start_x = water_tiles[0].x - dx
    start_y = water_tiles[0].y - dy
    end_x   = water_tiles[-1].x + dx
    end_y   = water_tiles[-1].y + dy
    for (ex, ey) in [(start_x, start_y), (end_x, end_y)]:
        if 0 <= ex < world_width and 0 <= ey < world_height:
            tile_objs3 = get_objects_at(placed_scenery, ex, ey)
            has_bridge = any(o.definition_id == BRIDGE_ID for o in tile_objs3)
            is_river   = any(o.definition_id == RIVER_ID  for o in tile_objs3)
            if not has_bridge and not is_river:
                bend = SceneryObject(ex, ey, BRIDGE_END_ID)
                append_scenery(placed_scenery, bend)
                mark_dirty_func(ex, ey)
                newly_placed.append(bend)

    return newly_placed

##############################################################################
# TILE EFFECT LOGIC
##############################################################################
def apply_tile_effects(player, tile_def_id, placed_scenery,
                       is_editor=False, world_width=100, world_height=60):
    if tile_def_id == PATH_ID:
        old_x, old_y = player.x, player.y
        player.move(player.last_move_direction, world_width, world_height, placed_scenery)
        # stops sliding if blocked