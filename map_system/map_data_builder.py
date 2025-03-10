# FileName: map_data_builder.py
# version: 3.3
# Summary: Higher-level map data read (JSON) and structure building, separate from UI code. Uses map_io_storage for the actual file ops.
# Tags: map, io


def build_map_data(placed_scenery, player=None,
                   world_width=100, world_height=100):
    """
    Builds a Python dict representing the map data, with optional player
    coordinates and the given world dimensions.

    'placed_scenery' can be:
      1) A dict-of-lists keyed by (x,y)
      2) A dict-of-dicts keyed by (x,y)
      3) A simple list of SceneryObjects

    Returns a dict with keys [world_width, world_height, scenery, player_x, player_y].
    """
    map_data = {
        "world_width": world_width,
        "world_height": world_height,
        "scenery": []
    }

    if player is not None:
        map_data["player_x"] = player.x
        map_data["player_y"] = player.y

    def add_scenery_obj(obj):
        if hasattr(obj, "x") and hasattr(obj, "y") and hasattr(obj, "definition_id"):
            map_data["scenery"].append({
                "x": obj.x,
                "y": obj.y,
                "definition_id": obj.definition_id
            })

    # If it's a dict, we might have nested or layered data
    if isinstance(placed_scenery, dict):
        for (tile_x, tile_y), tile_data in placed_scenery.items():
            if isinstance(tile_data, list):
                # Old-style: list of objects
                for obj in tile_data:
                    add_scenery_obj(obj)
            elif isinstance(tile_data, dict):
                # Possibly layered data
                for layer_key, layer_val in tile_data.items():
                    if isinstance(layer_val, list):
                        for obj in layer_val:
                            add_scenery_obj(obj)
                    else:
                        add_scenery_obj(layer_val)
            else:
                # skip if not recognized
                pass
    else:
        # If it's just a list
        for obj in placed_scenery:
            add_scenery_obj(obj)

    return map_data