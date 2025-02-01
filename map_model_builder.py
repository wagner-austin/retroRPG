# FileName: map_model_builder.py
# version: 1.0
#
# Summary: Shared logic for reading map data (dict or JSON file),
#          constructing a GameModel, and returning (model, context).
#          Used by play_runner.py, editor code, etc.
#
# Tags: map, model, builder

import os
import json

from map_io_storage import parse_map_dict
from player_char import Player
from player_char_io import load_player
from scenery_core import SceneryObject, ensure_layered_format
from model_main import GameModel, GameContext

def build_model_common(filename_or_data, is_generated, mode_name):
    """
    A helper that does the heavy lifting of:
      1) Loading raw map data from a dict or from 'maps/filename.json'
      2) parse_map_dict() => extracting width, height, scenery
      3) Loading (or creating) a Player object
      4) Positioning & clamping player
      5) Converting scenery into the layered 'placed_scenery' format
      6) Building the GameModel and a GameContext with the given mode_name

    :param filename_or_data: str (map file name) OR dict (raw JSON data)
    :param is_generated: bool, if True => place player in center for new map
    :param mode_name: str, e.g. "play" or "editor"
    :return: (GameModel, GameContext) or (None, None) if loading fails
    """
    raw_data = None
    model_filename = None

    # 1) Read JSON or use an existing dict
    if isinstance(filename_or_data, dict):
        raw_data = filename_or_data
    else:
        model_filename = filename_or_data
        load_path = os.path.join("maps", filename_or_data)
        try:
            with open(load_path, "r") as f:
                raw_data = json.load(f)
        except:
            # If file read fails, return None
            return None, None

    # 2) Parse map data
    map_data = parse_map_dict(raw_data)
    world_width = map_data["world_width"]
    world_height = map_data["world_height"]
    sinfo = map_data["scenery"]

    # 3) Load or create player
    player = load_player() or Player()

    # 4) Position the player
    if is_generated:
        # Place at center for brand-new or procedurally generated maps
        player.x = world_width // 2
        player.y = world_height // 2
    else:
        # Use the JSON-stored coords if present
        px = raw_data.get("player_x", None)
        py = raw_data.get("player_y", None)
        if px is not None and py is not None:
            player.x = px
            player.y = py

    # Clamp player location within the map boundaries
    player.x = max(0, min(player.x, world_width - 1))
    player.y = max(0, min(player.y, world_height - 1))

    # 5) Convert the list of scenery into layered format
    placed_scenery = {}
    for s in sinfo:
        if "definition_id" in s:
            x, y = s["x"], s["y"]
            obj = SceneryObject(x, y, s["definition_id"])
            placed_scenery.setdefault((x, y), []).append(obj)
    placed_scenery = ensure_layered_format(placed_scenery)

    # 6) Build the model & context
    model = GameModel()
    model.player = player
    model.placed_scenery = placed_scenery
    model.world_width = world_width
    model.world_height = world_height
    model.loaded_map_filename = model_filename  # Could be None if brand-new

    context = GameContext(mode_name=mode_name)

    return model, context
