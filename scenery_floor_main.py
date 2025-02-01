# FileName: scenery_floor_main.py
# version: 3.7
# Summary: Manages floor tiles (River, Grass, Path, etc.), collision checks, 
#          layered format, and tile effects. Duplicated placement logic is removed.
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

from layer_defs import (
    FLOOR_LAYER, OBJECTS_LAYER, ITEMS_LAYER, ENTITIES_LAYER,
    layer_for_def_id
)

# We still define register_scenery, get_placeable_scenery_defs, etc.
# The "placement" logic now lives in scenery_placement_utils.

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
    def __init__(self, x, y, paramA, paramB=None):
        self.x = x
        self.y = y
        self.definition_id = None
        self.char = "?"
        self.color_pair = 0

        if not hasattr(self.__class__, "_forward_cache"):
            self.__class__._forward_cache = build_forward_map()
            self.__class__._reverse_cache = build_reverse_map()

        forward_map = self.__class__._forward_cache
        reverse_map = self.__class__._reverse_cache

        if paramB is None:
            # paramA is the def_id
            def_id = paramA
            self.definition_id = def_id
            char_col = forward_map.get(def_id, ("?", 0))
            self.char = char_col[0]
            self.color_pair = char_col[1]
        else:
            # paramA is a char, paramB is a color
            c = paramA
            col = paramB
            self.char = c
            self.color_pair = col
            self.definition_id = reverse_map.get((c, col), None)

##############################################################################
# LAYER-BASED DICTIONARY & HELPER FUNCTIONS
##############################################################################
def ensure_layered_format(placed_scenery):
    if not placed_scenery:
        return placed_scenery

    first_key = next(iter(placed_scenery))
    first_val = placed_scenery[first_key]

    if isinstance(first_val, dict) and FLOOR_LAYER in first_val:
        return placed_scenery

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
            which_layer = layer_for_def_id(obj.definition_id)
            if which_layer == FLOOR_LAYER:
                tile_dict[FLOOR_LAYER] = obj
            else:
                tile_dict[which_layer].append(obj)
        new_dict[(x, y)] = tile_dict

    return new_dict

def _init_tile_layers(placed_scenery, x, y):
    if (x, y) not in placed_scenery:
        placed_scenery[(x, y)] = {
            FLOOR_LAYER:   None,
            OBJECTS_LAYER: [],
            ITEMS_LAYER:   [],
            ENTITIES_LAYER: [],
            '_prev_floor': None
        }
    else:
        tile_layers = placed_scenery[(x, y)]
        for key in [FLOOR_LAYER, OBJECTS_LAYER, ITEMS_LAYER, ENTITIES_LAYER, '_prev_floor']:
            if key not in tile_layers:
                if key in (FLOOR_LAYER, '_prev_floor'):
                    tile_layers[key] = None
                else:
                    tile_layers[key] = []

def append_scenery(placed_scenery, obj):
    x, y = obj.x, obj.y
    _init_tile_layers(placed_scenery, x, y)
    tile_layers = placed_scenery[(x, y)]
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
    x, y = obj.x, obj.y
    if (x, y) not in placed_scenery:
        return

    tile_layers = placed_scenery[(x, y)]
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
    else:
        if obj in tile_layers[layer_name]:
            tile_layers[layer_name].remove(obj)

    if (tile_layers[FLOOR_LAYER] is None and
        not tile_layers[OBJECTS_LAYER] and
        not tile_layers[ITEMS_LAYER] and
        not tile_layers[ENTITIES_LAYER]):
        tile_layers[FLOOR_LAYER] = SceneryObject(x, y, EMPTY_FLOOR_ID)
        tile_layers['_prev_floor'] = None

def get_objects_at(placed_scenery, x, y):
    if (x, y) not in placed_scenery:
        return []
    tile_layers = placed_scenery[(x, y)]
    merged = []
    if tile_layers[FLOOR_LAYER]:
        merged.append(tile_layers[FLOOR_LAYER])
    merged.extend(tile_layers[OBJECTS_LAYER])
    merged.extend(tile_layers[ITEMS_LAYER])
    merged.extend(tile_layers[ENTITIES_LAYER])
    return merged

##############################################################################
# COLLISION & LOOKUP
##############################################################################
def is_blocked(x, y, placed_scenery):
    merged_stack = get_objects_at(placed_scenery, x, y)
    if not merged_stack:
        return False
    top_obj = merged_stack[-1]
    info = ALL_SCENERY_DEFS.get(top_obj.definition_id, None)
    return bool(info and info.get("blocking", False))

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
# TILE EFFECT LOGIC
##############################################################################
def apply_tile_effects(player, tile_def_id, placed_scenery,
                       is_editor=False, world_width=100, world_height=60):
    """
    Example of how you could invoke special 'slide' effects or other triggers
    based on tile definition ID.
    """
    if tile_def_id == PATH_ID:
        old_x, old_y = player.x, player.y
        player.move(player.last_move_direction, world_width, world_height, placed_scenery)
        # If blocked, the move won't succeed, effectively ending the 'slide'.

# NOTE: The repeated place_tree / place_bridge_across_river / etc.
#       logic is now in scenery_placement_utils, so it's removed here.
