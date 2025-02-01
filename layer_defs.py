# FileName: layer_defs.py
# version: 1.1
# Summary: Defines layer constants and logic to determine which layer an ID belongs to.
# Tags: layers, definitions

from scenery_defs import (
    TREE_TRUNK_ID, TREE_TOP_ID, ROCK_ID, BRIDGE_ID, BRIDGE_END_ID,
    RIVER_ID, GRASS_ID, PATH_ID, SEMICOLON_FLOOR_ID, EMPTY_FLOOR_ID
)

#############################
# GAME LAYERS (z=10..12)
#############################
FLOOR_LAYER    = "floor"    # z=10
ITEMS_LAYER = "items" #z = 11
OBJECTS_LAYER  = "objects"  # z=12
ENTITIES_LAYER = "entities" # z=13

#############################
# UI LAYERS (z=100..101)
#############################
UI_HUD_LAYER   = "ui_hud"   # z=100
UI_MENU_LAYER  = "ui_menu"  # z=101


#############################
# TYPE SETS
#############################
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
    # Fallback layer if unknown
    return OBJECTS_LAYER