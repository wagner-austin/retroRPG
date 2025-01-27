# FileName: map_io_main.py
# version: 2.3 (MODULARIZED + now storing/loading player coords)

import os
import json
import curses

# Our UI modules:
from map_io_ui import (
    prompt_for_filename,
    display_map_list,
    display_map_list_for_save
)

# Our JSON storage/parsing modules:
from map_io_storage import (
    parse_map_dict,
    load_map_file,
    save_map_file
)

from procedural_map_generator.generator import generate_procedural_map


def load_map(stdscr):
    """
    Prompts the user to select or generate a map (curses-based UI).
    Returns:
      - "" if canceled
      - "GENERATE" or ("EDIT_GENERATE", None) if user chooses to generate
      - ("EDIT", filename) if user picks an existing map for editing
      - a map filename (string) if user picks an existing map to play
      - or a dict if "GENERATE" was chosen (the new map data)
    """
    selection = display_map_list(stdscr)
    if not selection:
        return ""

    # If user picked ENTER on "Generate a new map"
    if selection == "GENERATE":
        # Generate a brand-new map and return its data (dict)
        return generate_procedural_map()

    # If user pressed 'e' on "Generate" or on an existing file
    if isinstance(selection, tuple):
        # e.g., ("EDIT_GENERATE", None) => user wants to generate for editing
        #       ("EDIT", filename) => user wants to edit an existing file
        if selection[0] == "EDIT_GENERATE":
            data = generate_procedural_map()
            # Return a tuple that play_main.py recognizes
            return ("EDIT_GENERATE", data)
        elif selection[0] == "EDIT":
            return ("EDIT", selection[1])
        return ""

    # Otherwise, user picked an existing map to play (string filename)
    return selection


def save_map(stdscr, placed_scenery, player=None,
             world_width=100, world_height=100):
    """
    Prompt user to pick overwrite or new file, then save as JSON.
    We store scenery, dimensions, and optionally the player's coordinates.
    
    :param player: if provided, we'll save player_x, player_y in the file.
    """
    overwrite_or_new = display_map_list_for_save(stdscr)
    if not overwrite_or_new:
        return  # user canceled saving

    if overwrite_or_new == "NEW_FILE":
        filename = prompt_for_filename(stdscr, "Enter filename to save as: ")
        if not filename:
            return
        if not filename.endswith(".json"):
            filename += ".json"
    else:
        filename = overwrite_or_new

    maps_dir = "maps"
    save_path = os.path.join(maps_dir, filename)

    map_data = {
        "world_width": world_width,
        "world_height": world_height,
        "scenery": []
    }

    # If we have a player, store their coordinates for future loads
    if player is not None:
        map_data["player_x"] = player.x
        map_data["player_y"] = player.y

    # Convert placed_scenery (which may be a list or dict-of-lists) to a list
    # of JSON-friendly objects
    # If your engine already standardizes to a dict-of-lists, just iterate it safely
    if isinstance(placed_scenery, dict):
        # dict-of-lists: (x, y) -> [SceneryObject, ...]
        for (x, y), obj_list in placed_scenery.items():
            for obj in obj_list:
                map_data["scenery"].append({
                    "x": obj.x,
                    "y": obj.y,
                    "definition_id": obj.definition_id
                })
    else:
        # fallback if it's a simple list
        for obj in placed_scenery:
            map_data["scenery"].append({
                "x": obj.x,
                "y": obj.y,
                "definition_id": obj.definition_id
            })

    save_map_file(save_path, map_data)


def parse_map_dict_wrapper(raw_dict):
    """
    Thin wrapper around parse_map_dict that also extracts optional player coords.
    
    Returns a dict with:
      - "world_width", "world_height"
      - "scenery" (list of dicts)
      - "player_x", "player_y" (could be None if not found)
      or any other fields parse_map_dict includes.
      
    It's up to the caller to actually place the player using these coords,
    or to default them to center if missing.
    """
    data = parse_map_dict(raw_dict)

    # Attempt to pull player coords from the raw dict (if present)
    data["player_x"] = raw_dict.get("player_x", None)
    data["player_y"] = raw_dict.get("player_y", None)

    return data