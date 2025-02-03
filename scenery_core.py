# FileName: scenery_core.py
# version: 4.1
# Summary: Core scenery logic: a base SceneryObject class, plus layering & collision functions.
# Tags: scenery, core

# If you still have these constants somewhere, or replaced them with your new system, adjust accordingly:
from layer_defs import (
    FLOOR_LAYER, OBJECTS_LAYER, ENTITIES_LAYER,  # If you need them
    # e.g., ITEMS_LAYER if you have one
    layer_for_def_id
)
# Import your unified definitions from scenery_defs or scenery_manager
from scenery_defs import ALL_SCENERY_DEFS

EMPTY_FLOOR_ID = "EmptyFloor"  # so we can default to a blank floor tile if needed

class SceneryObject:
    def __init__(self, x, y, definition_id):
        """
        A simpler constructor that directly uses a definition ID, without the
        old forward/reverse maps. We can still store 'char' and 'color_pair'
        from ALL_SCENERY_DEFS if desired.
        """
        self.x = x
        self.y = y
        self.definition_id = definition_id
        self.char = "?"
        self.color_pair = "white_on_black"

        # Optionally, if you want to read default ASCII/ color from ALL_SCENERY_DEFS:
        info = ALL_SCENERY_DEFS.get(definition_id, {})
        self.char = info.get("ascii_char", "?")
        self.color_pair = info.get("color_name", "white_on_black")


def ensure_layered_format(placed_scenery):
    """
    Convert any old list-of-objects format => dict-of-layers format if needed.
    """
    if not placed_scenery:
        return placed_scenery

    first_key = next(iter(placed_scenery))
    first_val = placed_scenery[first_key]

    if isinstance(first_val, dict) and FLOOR_LAYER in first_val:
        # Already layered
        return placed_scenery

    new_dict = {}
    for (x, y), obj_list in placed_scenery.items():
        tile_dict = {
            FLOOR_LAYER:    None,
            OBJECTS_LAYER:  [],
            # If you have an ITEMS_LAYER, add it here too
            ENTITIES_LAYER: [],
            '_prev_floor':  None
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
    """
    Ensure placed_scenery[(x,y)] has the required layer structure.
    """
    if (x, y) not in placed_scenery:
        placed_scenery[(x, y)] = {
            FLOOR_LAYER:    None,
            OBJECTS_LAYER:  [],
            ENTITIES_LAYER: [],
            '_prev_floor':  None
        }
        # If you have an ITEMS_LAYER, add it here
        # e.g. "items": []
    else:
        tile_layers = placed_scenery[(x, y)]
        for key in [FLOOR_LAYER, OBJECTS_LAYER, ENTITIES_LAYER, '_prev_floor']:
            if key not in tile_layers:
                tile_layers[key] = None if key in (FLOOR_LAYER, '_prev_floor') else []

def append_scenery(placed_scenery, obj):
    """
    Place a new object into the correct layer for its definition.
    """
    x, y = obj.x, obj.y
    _init_tile_layers(placed_scenery, x, y)
    tile_layers = placed_scenery[(x, y)]

    layer_name = layer_for_def_id(obj.definition_id)

    if layer_name == FLOOR_LAYER:
        if (tile_layers[FLOOR_LAYER]
            and tile_layers[FLOOR_LAYER].definition_id != obj.definition_id):
            # push current floor into _prev_floor
            tile_layers['_prev_floor'] = tile_layers[FLOOR_LAYER]
        tile_layers[FLOOR_LAYER] = obj
    else:
        # Ensure floor isn't None
        if tile_layers[FLOOR_LAYER] is None:
            tile_layers[FLOOR_LAYER] = SceneryObject(x, y, EMPTY_FLOOR_ID)
        tile_layers[layer_name].append(obj)

def remove_scenery(placed_scenery, obj):
    """
    Remove a SceneryObject from its tile. If it's the floor, restore _prev_floor if available.
    If tile becomes fully empty, revert to EMPTY_FLOOR.
    """
    x, y = obj.x, obj.y
    if (x, y) not in placed_scenery:
        return

    tile_layers = placed_scenery[(x, y)]
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

    # If it is now completely empty, revert to an EMPTY_FLOOR
    if (tile_layers[FLOOR_LAYER] is None
        and not tile_layers[OBJECTS_LAYER]
        and not tile_layers[ENTITIES_LAYER]):
        tile_layers[FLOOR_LAYER] = SceneryObject(x, y, EMPTY_FLOOR_ID)
        tile_layers['_prev_floor'] = None

def get_objects_at(placed_scenery, x, y):
    """
    Return all objects in this tile, from floor to top.
    """
    if (x, y) not in placed_scenery:
        return []
    tile = placed_scenery[(x, y)]
    merged = []
    if tile[FLOOR_LAYER]:
        merged.append(tile[FLOOR_LAYER])
    merged.extend(tile[OBJECTS_LAYER])
    merged.extend(tile[ENTITIES_LAYER])
    # if you have an ITEMS_LAYER, merge it too
    return merged

def get_topmost_obj(placed_scenery, x, y):
    stack = get_objects_at(placed_scenery, x, y)
    return stack[-1] if stack else None

def get_scenery_def_id_at(x, y, placed_scenery):
    top = get_topmost_obj(placed_scenery, x, y)
    return top.definition_id if top else None

def get_scenery_color_at(x, y, placed_scenery):
    top = get_topmost_obj(placed_scenery, x, y)
    return getattr(top, "color_pair", "white_on_black") if top else "white_on_black"

def is_blocked(x, y, placed_scenery):
    """
    If there's nothing here, it's not blocked. Otherwise, check the top object's 'blocking' property.
    """
    stack = get_objects_at(placed_scenery, x, y)
    if not stack:
        return False
    top_obj = stack[-1]
    info = ALL_SCENERY_DEFS.get(top_obj.definition_id, {})
    return bool(info.get("blocking", False))