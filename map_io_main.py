# FileName: map_io_main.py
# version: 2.4 (Adds filename_override to skip prompt & overwrite existing file)

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

    if selection == "GENERATE":
        return generate_procedural_map()

    if isinstance(selection, tuple):
        if selection[0] == "EDIT_GENERATE":
            data = generate_procedural_map()
            return ("EDIT_GENERATE", data)
        elif selection[0] == "EDIT":
            return ("EDIT", selection[1])
        return ""

    return selection


def save_map(stdscr, placed_scenery, player=None,
             world_width=100, world_height=100,
             filename_override=None):
    """
    Saves the current map. If 'filename_override' is given, we skip the prompt
    and overwrite that file. Otherwise, we prompt the user for which file
    to overwrite or to create a new one.

    :param player: if provided, we store player coords as well.
    """
    if filename_override:
        # Overwrite existing file
        filename = filename_override
    else:
        # Prompt user for new or existing file
        overwrite_or_new = display_map_list_for_save(stdscr)
        if not overwrite_or_new:
            return  # user canceled

        if overwrite_or_new == "NEW_FILE":
            filename = prompt_for_filename(stdscr, "Enter filename to save as: ")
            if not filename:
                return
            if not filename.endswith(".json"):
                filename += ".json"
        else:
            # user picked an existing file from the list
            filename = overwrite_or_new

    maps_dir = "maps"
    save_path = os.path.join(maps_dir, filename)

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
        for obj in placed_scenery:
            map_data["scenery"].append({
                "x": obj.x,
                "y": obj.y,
                "definition_id": obj.definition_id
            })

    save_map_file(save_path, map_data)