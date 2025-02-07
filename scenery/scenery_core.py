# FileName: scenery_core.py
# version: 4.3.1 (modified to prevent alternating floor tiles)
#
# Summary: Core scenery logic: a base SceneryObject class, plus layering & collision functions.
# Tags: scenery, core

from scenery.scenery_manager import ALL_SCENERY_DEFS, layer_for_def_id

# Uncommented / re-enabled so that fallback floors can be placed correctly.
EMPTY_FLOOR_ID = "EmptyFloor"  # used as a fallback if a tile has no floor

class SceneryObject:
    def __init__(self, x, y, definition_id):
        """
        A simpler constructor that directly uses a definition ID.
        We can store 'char' and 'color_pair' from ALL_SCENERY_DEFS if desired.
        """
        self.x = x
        self.y = y
        self.definition_id = definition_id

        self.char = "?"
        self.color_pair = "white_on_black"

        # Look up default ASCII/color in ALL_SCENERY_DEFS
        info = ALL_SCENERY_DEFS.get(definition_id, {})
        self.char = info.get("ascii_char", "?")
        self.color_pair = info.get("color_name", "white_on_black")


def ensure_layered_format(placed_scenery):
    """
    Convert any old list-of-objects format => dict-of-layers format if needed.

    Old format: placed_scenery[(x, y)] = [obj1, obj2, ...]
    New format: placed_scenery[(x, y)] = {
        "floor": None or SceneryObject,
        "_prev_floor": None or SceneryObject,
        "objects": [SceneryObject, ...],
        "items": [...],
        "entities": [...],
        # etc.
    }
    """
    if not placed_scenery:
        return placed_scenery

    # Peek at one tile's value to see if it's already in the dict-of-layers format.
    first_key = next(iter(placed_scenery))
    first_val = placed_scenery[first_key]
    # If it's a dict and has a "floor" key, we'll consider it "layered."
    if isinstance(first_val, dict) and "floor" in first_val:
        return placed_scenery

    # Otherwise, convert it:
    new_dict = {}
    for (x, y), obj_list in placed_scenery.items():
        tile_dict = {
            "floor": None,
            "_prev_floor": None
        }
        # We iterate over the old objects and place each one by its layer
        for obj in obj_list:
            layer_name = layer_for_def_id(obj.definition_id)
            if layer_name == "floor":
                # Overriding any existing floor to prevent alternating floors.
                # Legacy code (commented out):
                # if tile_dict["floor"] is not None:
                #     tile_dict["_prev_floor"] = tile_dict["floor"]
                # tile_dict["floor"] = obj
                tile_dict["floor"] = obj
                tile_dict["_prev_floor"] = None
            else:
                if layer_name not in tile_dict:
                    tile_dict[layer_name] = []
                tile_dict[layer_name].append(obj)
        new_dict[(x, y)] = tile_dict

    return new_dict


def _init_tile_layers(placed_scenery, x, y):
    """
    Ensure placed_scenery[(x,y)] has at least a "floor" and "_prev_floor".
    Other layers will be created as needed when we place objects/items/entities.
    """
    if (x, y) not in placed_scenery:
        placed_scenery[(x, y)] = {
            "floor": None,
            "_prev_floor": None
        }
    else:
        tile_dict = placed_scenery[(x, y)]
        if "floor" not in tile_dict:
            tile_dict["floor"] = None
        if "_prev_floor" not in tile_dict:
            tile_dict["_prev_floor"] = None


def append_scenery(placed_scenery, obj):
    """
    Place a new object into the correct layer for its definition.
    If it's a floor tile, override any existing floor to prevent toggling.
    """
    x, y = obj.x, obj.y
    _init_tile_layers(placed_scenery, x, y)
    tile_dict = placed_scenery[(x, y)]

    layer_name = layer_for_def_id(obj.definition_id)

    if layer_name == "floor":
        # Overriding any existing floor to avoid alternating floors.
        # Legacy logic (commented out):
        # if tile_dict["floor"] and tile_dict["floor"].definition_id != obj.definition_id:
        #     tile_dict["_prev_floor"] = tile_dict["floor"]
        # tile_dict["floor"] = obj
        tile_dict["floor"] = obj
        tile_dict["_prev_floor"] = None
    else:
        # Ensure we have a floor (even if it's EmptyFloor) so the tile isn't blank
        if tile_dict["floor"] is None:
            tile_dict["floor"] = SceneryObject(x, y, EMPTY_FLOOR_ID)
        # Ensure the layer is a list
        if layer_name not in tile_dict:
            tile_dict[layer_name] = []
        tile_dict[layer_name].append(obj)


def remove_scenery(placed_scenery, obj):
    """
    Remove a SceneryObject from its tile. If it's the floor, restore _prev_floor
    if available. If the tile ends up totally empty, revert to an EMPTY_FLOOR tile.
    """
    x, y = obj.x, obj.y
    if (x, y) not in placed_scenery:
        return

    tile_dict = placed_scenery[(x, y)]
    layer_name = layer_for_def_id(obj.definition_id)

    if layer_name == "floor":
        if tile_dict.get("floor") == obj:
            if tile_dict.get("_prev_floor"):
                tile_dict["floor"] = tile_dict["_prev_floor"]
                tile_dict["_prev_floor"] = None
            else:
                tile_dict["floor"] = None
    else:
        if layer_name in tile_dict and obj in tile_dict[layer_name]:
            tile_dict[layer_name].remove(obj)

    # Check if the tile is now completely empty (no floor, no objects, etc.).
    is_empty = (tile_dict["floor"] is None)
    for k, v in tile_dict.items():
        if k in ("floor", "_prev_floor"):
            continue
        if isinstance(v, list) and len(v) > 0:
            is_empty = False
            break

    # If empty, revert to an EMPTY_FLOOR tile
    if is_empty:
        tile_dict["floor"] = SceneryObject(x, y, EMPTY_FLOOR_ID)
        tile_dict["_prev_floor"] = None


def get_objects_at(placed_scenery, x, y):
    """
    Return all objects in this tile, from the floor (bottom) up to the topmost layer.
    """
    if (x, y) not in placed_scenery:
        return []

    tile_dict = placed_scenery[(x, y)]
    merged = []

    # Floor is always at the bottom
    if tile_dict.get("floor"):
        merged.append(tile_dict["floor"])

    # Collect every other layer except '_prev_floor'
    for layer_key, layer_value in tile_dict.items():
        if layer_key in ("floor", "_prev_floor"):
            continue
        if isinstance(layer_value, list):
            merged.extend(layer_value)

    return merged


def get_topmost_obj(placed_scenery, x, y):
    """
    Return whichever SceneryObject is 'on top' (the last in the stacked layers).
    """
    stack = get_objects_at(placed_scenery, x, y)
    return stack[-1] if stack else None


def get_scenery_def_id_at(x, y, placed_scenery):
    """
    Return the definition_id of the topmost object at (x, y).
    """
    top_obj = get_topmost_obj(placed_scenery, x, y)
    return top_obj.definition_id if top_obj else None


def get_scenery_color_at(x, y, placed_scenery):
    """
    Return the color_pair of the topmost object at (x, y).
    """
    top_obj = get_topmost_obj(placed_scenery, x, y)
    return top_obj.color_pair if top_obj else "white_on_black"


def is_blocked(x, y, placed_scenery):
    """
    If there's nothing here, it's not blocked. Otherwise, check the top object's
    'blocking' field in ALL_SCENERY_DEFS.
    """
    top_obj = get_topmost_obj(placed_scenery, x, y)
    if not top_obj:
        return False
    tile_info = ALL_SCENERY_DEFS.get(top_obj.definition_id, {})
    return bool(tile_info.get("blocking", False))