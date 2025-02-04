# FileName: layer_manager.py
# version: 1.1
# Summary: A simple manager for layer info (name, z-order, visibility).
# Tags: layers, manager

# layer_manager.py

LAYER_CONFIG = {
    "floor":    {"z_index": 10,  "description": "Floor tiles"},
    "objects":  {"z_index": 20,  "description": "Solid objects on top of floors"},
    "items":    {"z_index": 30,  "description": "Loose items"},
    "entities": {"z_index": 40,  "description": "NPCs / player layer"},
    "overhead": {"z_index": 50,  "description": "Overhead canopies, etc."},
    "ui_hud":   {"z_index": 100, "description": "HUD / overlay UI"},
    "ui_menu":  {"z_index": 110, "description": "Menu overlays"},
}

def get_layer_zindex(layer_name: str) -> int:
    layer_info = LAYER_CONFIG.get(layer_name)
    if layer_info is None:
        return 999  # fallback if unknown
    return layer_info["z_index"]

def get_layers_in_draw_order() -> list:
    """
    Return all layer names sorted by their z_index ascending.
    """
    return sorted(LAYER_CONFIG.keys(), key=lambda ln: LAYER_CONFIG[ln]["z_index"])    