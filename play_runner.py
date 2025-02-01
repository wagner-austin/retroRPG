# FileName: play_runner.py
# version: 3.2
#
# Summary: Helper for loading map data, building a GameModel & GameContext. 
#          Ensures that newly placed scenery in editor mode is saved correctly.
#
# Tags: play, runner, map, editor

import os
import json

from map_io_storage import parse_map_dict
from player_char import Player
from player_char_io import load_player
from scenery_core import SceneryObject, ensure_layered_format
from model_main import GameModel, GameContext

def build_model_for_play(filename_or_data, is_generated=False):
    """
    Loads map data (if 'filename_or_data' is a filename) or uses
    the dict provided (e.g. from a procedural generator),
    then builds a GameModel & a 'play' context.
    
    Returns (model, context). If loading fails, returns (None, None).
    """
    raw_data = None
    model_filename = None

    # 1) Read JSON or use existing dict
    if isinstance(filename_or_data, dict):
        # We already have a raw dict (e.g. from a procedural generator)
        raw_data = filename_or_data
    else:
        # It's a filename; read JSON from "maps" directory
        model_filename = filename_or_data
        maps_dir = "maps"
        load_path = os.path.join(maps_dir, filename_or_data)
        try:
            with open(load_path, "r") as f:
                raw_data = json.load(f)
        except:
            # If loading fails, just return (None, None)
            return None, None

    # 2) Parse map data
    map_data = parse_map_dict(raw_data)
    world_width = map_data["world_width"]
    world_height = map_data["world_height"]
    sinfo = map_data["scenery"]

    # 3) Load or create player
    player = load_player()
    if not player:
        player = Player()

    # Position player
    if is_generated:
        # Place at center for brand-new (procedural) maps
        player.x = world_width // 2
        player.y = world_height // 2
    else:
        # Use stored x,y if the JSON provided them
        px = raw_data.get("player_x", None)
        py = raw_data.get("player_y", None)
        if px is not None and py is not None:
            player.x = px
            player.y = py

    # Clamp to map bounds
    player.x = max(0, min(player.x, world_width - 1))
    player.y = max(0, min(player.y, world_height - 1))

    # 4) Convert the list of scenery into layered format
    placed_scenery = {}
    for s in sinfo:
        if "definition_id" in s:
            x, y = s["x"], s["y"]
            obj = SceneryObject(x, y, s["definition_id"])
            placed_scenery.setdefault((x, y), []).append(obj)
    placed_scenery = ensure_layered_format(placed_scenery)

    # 5) Build the model & context
    model = GameModel()
    model.player = player
    model.placed_scenery = placed_scenery
    model.world_width = world_width
    model.world_height = world_height

    # IMPORTANT FIX: Always store the filename, 
    # so we can overwrite it if the user quick-saves in editor or play mode.
    # If this was a brand-new generated map, model_filename remains None.
    model.loaded_map_filename = model_filename

    context = GameContext(mode_name="play")  # "play" => sliding, respawns, etc.
    return model, context


def build_model_for_editor(filename_or_data, is_generated=False):
    """
    Similar to build_model_for_play, but returns a model + 'editor' context
    for map editing. No curses usage here either.
    
    Returns (model, context) or (None, None) if loading fails.
    """
    raw_data = None
    model_filename = None

    # 1) Read JSON or use existing dict
    if isinstance(filename_or_data, dict):
        raw_data = filename_or_data
    else:
        model_filename = filename_or_data
        maps_dir = "maps"
        load_path = os.path.join(maps_dir, filename_or_data)
        try:
            with open(load_path, "r") as f:
                raw_data = json.load(f)
        except:
            return None, None

    # 2) Parse map data
    map_data = parse_map_dict(raw_data)
    world_width = map_data["world_width"]
    world_height = map_data["world_height"]
    sinfo = map_data["scenery"]

    # 3) Load or create player
    player = load_player()
    if not player:
        player = Player()

    # Position player
    if is_generated:
        player.x = world_width // 2
        player.y = world_height // 2
    else:
        px = raw_data.get("player_x", None)
        py = raw_data.get("player_y", None)
        if px is not None and py is not None:
            player.x = px
            player.y = py

    # Clamp to map bounds
    player.x = max(0, min(player.x, world_width - 1))
    player.y = max(0, min(player.y, world_height - 1))

    # 4) Convert scenery -> layered
    placed_scenery = {}
    for s in sinfo:
        if "definition_id" in s:
            x, y = s["x"], s["y"]
            obj = SceneryObject(x, y, s["definition_id"])
            placed_scenery.setdefault((x, y), []).append(obj)
    placed_scenery = ensure_layered_format(placed_scenery)

    # 5) Build the model & context
    model = GameModel()
    model.player = player
    model.placed_scenery = placed_scenery
    model.world_width = world_width
    model.world_height = world_height

    # Again, always store model_filename, even if generated => None.
    model.loaded_map_filename = model_filename

    # Editor context => no sliding, can place/undo objects, etc.
    context = GameContext(mode_name="editor")
    return model, context