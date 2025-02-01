# FileName: layer_defs.py
# Summary: Defines layer constants and logic to determine which layer an ID belongs to.

from scenery_defs import (
    TREE_TRUNK_ID, TREE_TOP_ID, ROCK_ID, BRIDGE_ID, BRIDGE_END_ID,
    RIVER_ID, GRASS_ID, PATH_ID, SEMICOLON_FLOOR_ID, EMPTY_FLOOR_ID
)

# Layer constants
FLOOR_LAYER    = "floor"
OBJECTS_LAYER  = "objects"
ITEMS_LAYER    = "items"
ENTITIES_LAYER = "entities"

# Type sets
FLOOR_TYPE_IDS = {
    RIVER_ID,
    GRASS_ID,
    PATH_ID,
    SEMICOLON_FLOOR_ID,
    EMPTY_FLOOR_ID,
}
OBJECT_TYPE_IDS = {
    ROCK_ID,
    TREE_TRUNK_ID,
    TREE_TOP_ID,
    BRIDGE_ID,
    BRIDGE_END_ID,
}
ITEM_TYPE_IDS = set()
ENTITIES_TYPE_IDS = set()

def layer_for_def_id(def_id):
    """
    Decide which layer an ID belongs to based on known sets.
    """
    if def_id in FLOOR_TYPE_IDS:
        return FLOOR_LAYER
    elif def_id in OBJECT_TYPE_IDS:
        return OBJECTS_LAYER
    elif def_id in ITEM_TYPE_IDS:
        return ITEMS_LAYER
    elif def_id in ENTITIES_TYPE_IDS:
        return ENTITIES_LAYER
    # Fallback layer for unknown IDs
    return OBJECTS_LAYER
