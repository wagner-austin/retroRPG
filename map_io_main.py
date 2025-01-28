# FileName: map_io_main.py
# version: 3.0
# Summary: Handles raw map data reading/writing (JSON) and structure building, no curses or UI logic.
# Tags: map, io

import os
import json

from map_io_storage import parse_map_dict, load_map_file, save_map_file


def load_map_data(filename):
    """
    Loads map data (JSON) from the given filename as a Python dict.
    Returns the loaded dict or None on failure.
    """
    try:
        return load_map_file(filename)
    except:
        return None


def build_map_data(placed_scenery, player=None, world_width=100, world_height=100):
    """
    Builds a Python dict representing the map data, with optional player
    coordinates and the given world dimensions. 'placed_scenery' can be either
    a dict-of-lists keyed by (x,y) or a list of objects with .x, .y attributes.
    """
    map_data = {
        "world_width": world_width,
        "world_height": world_height,
        "scenery": []
    }

    if player is not None:
        map_data["player_x"] = player.x
        map_data["player_y"] = player.y

    # Convert placed_scenery to a list of dicts
    if isinstance(placed_scenery, dict):
        for (x, y), obj_list in placed_scenery.items():
            for obj in obj_list:
                map_data["scenery"].append({
                    "x": obj.x,
                    "y": obj.y,
                    "definition_id": obj.definition_id
                })
    else:
        # If it's just a list, iterate directly
        for obj in placed_scenery:
            map_data["scenery"].append({
                "x": obj.x,
                "y": obj.y,
                "definition_id": obj.definition_id
            })

    return map_data