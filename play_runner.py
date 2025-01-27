# FileName: play_runner.py
# version: 1.8 (Robust fix: use player_x/player_y from map if not generated)

import os
import json
import curses

from player_char import Player
from player_char_io import load_player, save_player
from scenery_main import SceneryObject
from engine_main import run_engine, GameContext
# Import parse_map_dict and save_map so we can save after editing or playing
from map_io_main import parse_map_dict, save_map


def parse_and_run_editor(stdscr, filename_or_data, is_generated=False):
    """
    If filename_or_data is a dict => parse the map data directly,
    else load the JSON map from disk => parse => run editor mode.

    After the editor exits (user presses 'y'), we always save player data.
    If this map was generated (is_generated=True), we prompt if they want to save scenery.
    """
    # 1) Load or parse raw map data
    if isinstance(filename_or_data, dict):
        raw_data = filename_or_data
        model_filename = None  # new, so must prompt on quick-save
    else:
        model_filename = filename_or_data  # existing file => can overwrite
        maps_dir = "maps"
        load_path = os.path.join(maps_dir, filename_or_data)
        try:
            with open(load_path, "r") as f:
                raw_data = json.load(f)
        except:
            return

    # 2) Convert raw dict -> structured map_data
    map_data = parse_map_dict(raw_data)
    world_width = map_data["world_width"]
    world_height = map_data["world_height"]
    sinfo = map_data["scenery"]

    # 3) Load or create the Player
    player = load_player()  # from character/character_data.json
    if not player:
        player = Player()

    # 4) If newly generated, center player. Otherwise, if map_data has coords, use them.
    if is_generated:
        player.x = world_width // 2
        player.y = world_height // 2
    else:
        px = raw_data.get("player_x", None)
        py = raw_data.get("player_y", None)
        if px is not None and py is not None:
            player.x = px
            player.y = py

    # 5) Clamp to boundaries
    player.x = max(0, min(player.x, world_width - 1))
    player.y = max(0, min(player.y, world_height - 1))

    # 6) Build placed_scenery as a dict-of-lists
    placed_scenery = {}
    for s in sinfo:
        if "definition_id" in s:
            x, y = s["x"], s["y"]
            obj = SceneryObject(x, y, s["definition_id"])
            placed_scenery.setdefault((x, y), []).append(obj)

    # 7) Run the engine in 'editor' mode
    context = GameContext(mode_name="editor")
    run_engine(
        stdscr,
        context,
        player,
        placed_scenery,
        respawn_list=None,
        map_top_offset=3,
        world_width=world_width,
        world_height=world_height,
        loaded_map_filename=None if is_generated else model_filename
    )

    # 8) After user quits, save the player data
    save_player(player)

    # 9) If it's a generated map, prompt for saving
    if is_generated:
        ask_save_generated_map(
            stdscr,
            placed_scenery,
            world_width,
            world_height
        )


def parse_and_run_play(stdscr, filename_or_data, is_generated=False):
    """
    If it's a dict => parse directly (generated map),
    else load from file => parse => run "play" mode.

    After the user exits (press 'y'), we always save player data.
    If this map was generated (is_generated=True), prompt to save scenery.
    """
    if isinstance(filename_or_data, dict):
        # newly generated => must prompt on quick-save
        raw_data = filename_or_data
        model_filename = None
    else:
        # loaded from an existing file => can overwrite
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

    # 1) Load or create the Player
    player = load_player()
    if not player:
        player = Player()

    # 2) If newly generated, center. Else, if coords exist in file, use them.
    if is_generated:
        player.x = world_width // 2
        player.y = world_height // 2
    else:
        px = raw_data.get("player_x", None)
        py = raw_data.get("player_y", None)
        if px is not None and py is not None:
            player.x = px
            player.y = py

    # 3) Clamp
    player.x = max(0, min(player.x, world_width - 1))
    player.y = max(0, min(player.y, world_height - 1))

    # 4) Build placed_scenery
    placed_scenery = {}
    for s in sinfo:
        if "definition_id" in s:
            x, y = s["x"], s["y"]
            obj = SceneryObject(x, y, s["definition_id"])
            placed_scenery.setdefault((x, y), []).append(obj)

    # 5) Run the engine in 'play' mode
    ctx = GameContext(mode_name="play")
    run_engine(
        stdscr,
        ctx,
        player,
        placed_scenery,
        respawn_list=[],
        map_top_offset=3,
        world_width=world_width,
        world_height=world_height,
        loaded_map_filename=None if is_generated else model_filename
    )

    # 6) Once user quits, save the Player
    save_player(player)

    # 7) If it's a generated map, ask if they want to save
    if is_generated:
        ask_save_generated_map(
            stdscr,
            placed_scenery,
            world_width,
            world_height
        )


def ask_save_generated_map(stdscr, placed_scenery, world_width, world_height):
    """
    Displays a minimal yes/no prompt on the existing screen (no clear).
    If 'y', save scenery. Otherwise skip saving.
    """
    max_h, max_w = stdscr.getmaxyx()
    prompt = "Save this generated map? (y/n)"

    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    row = max_h - 2
    col = 2

    try:
        stdscr.addstr(row, col, prompt, curses.A_BOLD)
    except:
        pass
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key in (ord('y'), ord('Y')):
            save_map(stdscr, placed_scenery,
                     world_width=world_width,
                     world_height=world_height)
            break
        elif key in (ord('n'), ord('N'), ord('q'), 27):  # ESC
            break

    # Clean up the prompt
    try:
        stdscr.addstr(row, col, " " * len(prompt))
        stdscr.refresh()
    except:
        pass