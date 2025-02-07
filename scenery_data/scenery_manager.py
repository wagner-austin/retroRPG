# FileName: scenery_manager.py

# version 1.0

# Summary: Handles scenery defs

# Tags: scenery, manager

# Import each partial dictionary:
from scenery_data.floor_tiles import FLOOR_TILES
from scenery_data.object_tiles import OBJECT_TILES
from scenery_data.item_tiles import ITEM_TILES
from scenery_data.entity_tiles import ENTITY_TILES

def build_all_scenery_defs():
    combined = {}
    combined.update(FLOOR_TILES)
    combined.update(OBJECT_TILES)
    combined.update(ITEM_TILES)
    combined.update(ENTITY_TILES)
    return combined

ALL_SCENERY_DEFS = build_all_scenery_defs()

def layer_for_def_id(def_id: str) -> str:
    """
    Return the 'layer' string declared in the tile definition, 
    or 'objects' as a fallback if undefined.
    """
    info = ALL_SCENERY_DEFS.get(def_id, {})
    return info.get("layer", "objects")

def get_placeable_scenery_defs():
    """
    Return a list of def_ids from ALL_SCENERY_DEFS that have 'placeable': True
    """
    return [
        def_id
        for def_id, info in ALL_SCENERY_DEFS.items()
        if info.get("placeable", False)
    ]
