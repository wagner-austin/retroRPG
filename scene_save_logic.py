# FileName: scene_save_logic.py
# version: 1.0
#
# Summary: Contains logic extracted from curses_scene_save for:
#          - Saving player data
#          - Building and saving map data
#          - Updating player coordinates in map
#
# Tags: map, save, logic

import os
import json

from players.player_char_io import save_player
from map_system.map_data_builder import build_map_data
from map_system.map_io_storage import save_map_file
from map_system.map_list_logic import file_exists_in_maps_dir, MAPS_DIR  # use the common maps directory

def save_player_data(player):
    """
    Save the player's data (delegates to player_char_io.save_player).
    """
    save_player(player)

def does_file_exist_in_maps_dir(filename):
    """
    Check if a file with the given filename exists in the maps directory.
    """
    return file_exists_in_maps_dir(filename)

def build_and_save_map(filename, placed_scenery, player, world_width, world_height):
    """
    Build map data from the given scenery/player, then save it to disk in the maps folder.
    """
    map_data = build_map_data(
        placed_scenery,
        player=player,
        world_width=world_width,
        world_height=world_height
    )
    save_map_file(os.path.join(MAPS_DIR, filename), map_data)

def update_player_coords_in_map(filename, px, py):
    """
    Helper to store player's final x,y in an existing map JSON.
    If you want to store more (e.g. gold, wood, HP), add them here.
    """
    map_path = os.path.join(MAPS_DIR, filename)
    if not os.path.exists(map_path):
        return

    try:
        with open(map_path, "r") as f:
            data = json.load(f)

        data["player_x"] = px
        data["player_y"] = py

        save_map_file(map_path, data)
    except:
        pass