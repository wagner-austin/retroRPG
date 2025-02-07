# FileName: layer_manager.py
# version: 1.2
# Summary: A simple manager for layer info (name, z-order, visibility).
# Tags: layers, manager

LAYER_CONFIG = {
    # New layers for the home/main menu
    "home_background": {"z_index": 1,   "description": "Background for the home screen"},
    "home_menu":       {"z_index": 2,   "description": "Menu UI for the home screen"},

    # Existing layers for the in-game world
    "floor":    {"z_index": 10,  "description": "Floor tiles"},
    "objects":  {"z_index": 20,  "description": "Solid objects on top of floors"},
    "items":    {"z_index": 30,  "description": "Loose items"},
    "entities": {"z_index": 40,  "description": "NPCs / player layer"},
    "overhead": {"z_index": 50,  "description": "Overhead canopies, etc."},

    # Existing UI layers
    "ui_hud":   {"z_index": 100, "description": "HUD / overlay UI"},
    "ui_menu":  {"z_index": 110, "description": "In-game menu overlays"},
}

def get_layer_zindex(layer_name: str) -> int:
    """
    Return the numeric z-index for a given layer_name.
    If unknown, returns a fallback (999).
    """
    layer_info = LAYER_CONFIG.get(layer_name)
    if layer_info is None:
        return 999  # fallback if unknown
    return layer_info["z_index"]

def get_layers_in_draw_order() -> list:
    """
    Return all layer names sorted by their z_index ascending.
    """
    return sorted(LAYER_CONFIG.keys(), key=lambda ln: LAYER_CONFIG[ln]["z_index"])