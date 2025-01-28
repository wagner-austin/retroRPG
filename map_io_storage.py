# FileName: map_io_storage.py
# version: 1.0
# Summary: Handles the underlying JSON I/O logic for parsing and serializing map files, separate from UI code.
# Tags: map, io, storage

import os
import json

def parse_map_dict(raw_dict):
    """
    Takes a raw dictionary from JSON and extracts:
      world_width, world_height, scenery, extras
    ignoring any 'player' keys.
    """
    world_width = raw_dict.get("world_width", 100)
    world_height = raw_dict.get("world_height", 60)
    scenery = raw_dict.get("scenery", [])

    known_keys = {"world_width", "world_height", "scenery", "player"}
    extras = {}
    for k, v in raw_dict.items():
        if k not in known_keys:
            extras[k] = v

    return {
        "world_width": world_width,
        "world_height": world_height,
        "scenery": scenery,
        "extras": extras
    }

def load_map_file(filepath):
    """
    Reads a JSON file from 'filepath' and returns the parsed dict.
    Returns None if there's an error.
    """
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        return data
    except:
        return None

def save_map_file(filepath, map_data):
    """
    Writes 'map_data' (a dict with world_width, world_height, scenery, etc.)
    to JSON at 'filepath'. Ignores errors.
    """
    try:
        with open(filepath, "w") as f:
            json.dump(map_data, f)
    except:
        pass
