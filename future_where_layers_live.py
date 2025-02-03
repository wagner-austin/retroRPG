# FileName: future_where_layers_live.py
# version: 1.2
#
# Summary:
#   Single source of truth for:
#    - Layer names
#    - Their z-orders
#    - Visibility settings
#    - Which definition IDs belong to which layer
#
# Tags: layers, definitions

##############################################################################
# Layer name constants
##############################################################################
UI_EDITOR_OVERLAY_LAYER = "ui_editor_overlay"
LAYER_BACKGROUND = "background"
LAYER_GAME_WORLD = "game_world"

# If you treat floor/objects/items/entities/UI as full layers, define them here, too:
LAYER_FLOOR = "floor"       # (Previously: FLOOR_LAYER from layer_defs.py)
LAYER_OBJECTS = "objects"   # (Previously: OBJECTS_LAYER from layer_defs.py)
LAYER_ITEMS = "items"       # (Previously: ITEMS_LAYER from layer_defs.py)
LAYER_ENTITIES = "entities" # (Previously: ENTITIES_LAYER from layer_defs.py)

# Additional UI layers from layer_defs.py, retained here:
UI_HUD_LAYER  = "ui_hud"
UI_MENU_LAYER = "ui_menu"

##############################################################################
# All layer definitions
##############################################################################
ALL_LAYER_DEFS = {
    # Background layer
    LAYER_BACKGROUND: {
        "z_order": 0,
        "visible": True,
        "definition_ids": []
    },
    # Game world layer
    LAYER_GAME_WORLD: {
        "z_order": 10,
        "visible": True,
        "definition_ids": []
    },
    # Editor overlay
    UI_EDITOR_OVERLAY_LAYER: {
        "z_order": 102,
        "visible": True,
        "definition_ids": []
    },
    # HUD/UI layers
    UI_HUD_LAYER: {
        "z_order": 100,
        "visible": True,
        "definition_ids": []
    },
    UI_MENU_LAYER: {
        "z_order": 101,
        "visible": True,
        "definition_ids": []
    },

    # Floor layer (previously in layer_defs.py)
    LAYER_FLOOR: {
        "z_order": 20,
        "visible": True,
        "definition_ids": [
            # Copied from FLOOR_TYPE_IDS in layer_defs.py:
            "River",
            "Grass",
            "Path",
            "SemicolonFloor",
            "EmptyFloor",
        ]
    },
    # Objects layer (previously in layer_defs.py)
    LAYER_OBJECTS: {
        "z_order": 30,
        "visible": False,
        "definition_ids": [
            # Copied from OBJECT_TYPE_IDS in layer_defs.py:
            "Rock",
            "TreeTrunk",
            "TreeTop",
            "Bridge",
            "BridgeEnd",
        ]
    },
    # Items layer (previously in layer_defs.py)
    LAYER_ITEMS: {
        "z_order": 40,
        "visible": True,
        "definition_ids": [
            # Copied from ITEM_TYPE_IDS in layer_defs.py (currently empty)
        ]
    },
    # Entities layer (previously in layer_defs.py)
    LAYER_ENTITIES: {
        "z_order": 50,
        "visible": True,
        "definition_ids": [
            # Copied from ENTITIES_TYPE_IDS in layer_defs.py (currently empty)
        ]
    },
}