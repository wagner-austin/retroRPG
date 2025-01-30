# FileName: play_runner.py
# version: 3.0
# Summary: Orchestrates loading a map and calling the new engine loop for play or editor mode.
# Tags: play, runner, map, editor

import os
import json

from map_io_storage import parse_map_dict
from player_char import Player
from player_char_io import load_player, save_player
from scenery_main import SceneryObject, ensure_layered_format
from model_main import GameModel, GameContext

# Now we use the front-end classes for input & rendering, but do NOT import curses here.
from curses_frontend.curses_input import CursesGameInput
from curses_frontend.curses_renderer import CursesGameRenderer
from engine_main import run_game_loop

def parse_and_run_editor(stdscr, filename_or_data, is_generated=False):
    """
    Loads/parses the map data, sets up model in 'editor' mode,
    then calls run_game_loop with the curses front-end.
    """
    if isinstance(filename_or_data, dict):
        raw_data = filename_or_data
        model_filename = None
    else:
        model_filename = filename_or_data
        maps_dir = "maps"
        load_path = os.path.join(maps_dir, filename_or_data)
        try:
            with open(load_path, "r") as f:
                raw_data = json.load(f)
        except:
            return

    map_data = parse_map_dict(raw_data)
    world_width = map_data["world_width"]
    world_height = map_data["world_height"]
    sinfo = map_data["scenery"]

    # Load or create player
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

    # Clamp
    player.x = max(0, min(player.x, world_width - 1))
    player.y = max(0, min(player.y, world_height - 1))

    # Build placed_scenery
    placed_scenery = {}
    for s in sinfo:
        if "definition_id" in s:
            x, y = s["x"], s["y"]
            obj = SceneryObject(x, y, s["definition_id"])
            placed_scenery.setdefault((x, y), []).append(obj)

    # Convert old dict-of-lists into layered structure
    placed_scenery = ensure_layered_format(placed_scenery)

    # Create model & context
    model = GameModel()
    model.player = player
    model.placed_scenery = placed_scenery
    model.world_width = world_width
    model.world_height = world_height
    model.loaded_map_filename = None if is_generated else model_filename

    context = GameContext("editor")

    # Instantiate curses front-end
    game_input = CursesGameInput(stdscr)
    game_renderer = CursesGameRenderer(stdscr)

    # Enter the main logic loop
    run_game_loop(model, context, game_input, game_renderer)

    # Save player data
    save_player(player)

    # If not generated, store new coords
    if (not is_generated) and model_filename:
        maps_dir = "maps"
        map_path = os.path.join(maps_dir, model_filename)
        if os.path.exists(map_path):
            with open(map_path, "r") as f:
                existing_data = json.load(f)
            existing_data["player_x"] = player.x
            existing_data["player_y"] = player.y
            from map_io_storage import save_map_file
            save_map_file(map_path, existing_data)


def parse_and_run_play(stdscr, filename_or_data, is_generated=False):
    """
    Similar to parse_and_run_editor, but in 'play' mode.
    """
    if isinstance(filename_or_data, dict):
        raw_data = filename_or_data
        model_filename = None
    else:
        model_filename = filename_or_data
        maps_dir = "maps"
        load_path = os.path.join(maps_dir, filename_or_data)
        try:
            with open(load_path, "r") as f:
                raw_data = json.load(f)
        except:
            return

    map_data = parse_map_dict(raw_data)
    world_width = map_data["world_width"]
    world_height = map_data["world_height"]
    sinfo = map_data["scenery"]

    # Load/create player
    player = load_player()
    if not player:
        player = Player()

    if is_generated:
        player.x = world_width // 2
        player.y = world_height // 2
    else:
        px = raw_data.get("player_x", None)
        py = raw_data.get("player_y", None)
        if px is not None and py is not None:
            player.x = px
            player.y = py

    # Clamp
    player.x = max(0, min(player.x, world_width - 1))
    player.y = max(0, min(player.y, world_height - 1))

    # Build scenery => layered format
    placed_scenery = {}
    for s in sinfo:
        if "definition_id" in s:
            x, y = s["x"], s["y"]
            obj = SceneryObject(x, y, s["definition_id"])
            placed_scenery.setdefault((x, y), []).append(obj)
    placed_scenery = ensure_layered_format(placed_scenery)

    # Create model & context
    model = GameModel()
    model.player = player
    model.placed_scenery = placed_scenery
    model.world_width = world_width
    model.world_height = world_height
    model.loaded_map_filename = None if is_generated else model_filename

    context = GameContext("play")

    # Instantiate curses front-end
    game_input = CursesGameInput(stdscr)
    game_renderer = CursesGameRenderer(stdscr)

    # Start main logic loop
    run_game_loop(model, context, game_input, game_renderer)

    # Save player
    save_player(player)

    # If not generated, store new coords
    if (not is_generated) and model_filename:
        maps_dir = "maps"
        map_path = os.path.join(maps_dir, model_filename)
        if os.path.exists(map_path):
            with open(map_path, "r") as f:
                existing_data = json.load(f)
            existing_data["player_x"] = player.x
            existing_data["player_y"] = player.y
            from map_io_storage import save_map_file
            save_map_file(map_path, existing_data)