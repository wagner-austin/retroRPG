# FileName: layer_system.py
# version: 1.1
# Summary: Initializes layers in the LayerManager and provides a reverse lookup for def_id -> layer_name.
# Tags: layers, system

from where_layers_live import ALL_LAYER_DEFS

##############################################################################
# We'll build a reverse lookup: def_id -> layer_name
##############################################################################
_def_to_layer_map = {}

def init_layer_system(layer_manager):
    """
    1) Register each layer from ALL_LAYER_DEFS into the given layer_manager,
       setting z_order and visibility.
    2) Build a reverse map so we can do get_layer_for_def_id() quickly.
    """
    global _def_to_layer_map
    _def_to_layer_map = {}

    for layer_name, info in ALL_LAYER_DEFS.items():
        z = info["z_order"]
        vis = info["visible"]
        layer_manager.add_layer(layer_name, z, vis)

        for def_id in info["definition_ids"]:
            _def_to_layer_map[def_id] = layer_name

def get_layer_for_def_id(def_id):
    """
    Return which layer a given def_id belongs to, based on ALL_LAYER_DEFS.
    If not found, default to "objects" (the LAYER_OBJECTS string).
    """
    return _def_to_layer_map.get(def_id, "objects")