# FileName: layer_defs.py
# version: 1.3
# Summary: Defines layer constants and the sets of definition IDs that belong to each layer.
#          Also has `layer_for_def_id` to map a definition ID to the right layer.
# Tags: layers, definitions

# --------------------------
# 1) LAYER CONSTANTS
# --------------------------
FLOOR_LAYER    = "floor"      # z=10
ITEMS_LAYER = "items"
OBJECTS_LAYER  = "objects"    # z=11
ENTITIES_LAYER = "entities"   # z=12

UI_HUD_LAYER   = "ui_hud"     # z=100
UI_MENU_LAYER  = "ui_menu"    # z=101

# --------------------------
# 2) DEFINITION ID SETS
#    (No imports from scenery_* here!)
# --------------------------
FLOOR_TYPE_IDS = {
    "River",
    "Grass",
    "Path",
    "SemicolonFloor",
    "EmptyFloor",
}

OBJECT_TYPE_IDS = {
    "Rock",
    "TreeTrunk",
    "TreeTop",
    "Bridge",
    "BridgeEnd",
}

ITEM_TYPE_IDS = set()      # Add if you have item definition IDs
ENTITIES_TYPE_IDS = set()  # Add if you have entity definition IDs

# --------------------------
# 3) MAPPING FUNCTION
# --------------------------
def layer_for_def_id(def_id: str) -> str:
    """
    Return the layer name (floor, objects, etc.) for a given definition ID.
    """
    if def_id in FLOOR_TYPE_IDS:
        return FLOOR_LAYER
    elif def_id in OBJECT_TYPE_IDS:
        return OBJECTS_LAYER
    elif def_id in ITEM_TYPE_IDS:
        return ITEMS_LAYER
        # e.g. return "items"
        return "items"
    elif def_id in ENTITIES_TYPE_IDS:
        return ENTITIES_LAYER
    else:
        # Fallback if unknown
        return OBJECTS_LAYER
