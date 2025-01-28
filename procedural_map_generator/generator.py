# FileName: generator.py
# version: 2.0
# Summary: Coordinates the procedural generation workflow, calling sub-generators (rivers, grass, etc.) in order.
# Tags: map, generation, pipeline

import random
from collections import deque  # for BFS queue

# Import sub-generators from their respective modules
from .gen_rivers import spawn_rivers
from .gen_grass import (
    spawn_large_semicircle_grass,
    find_grass_regions,
    find_random_grass_spot
)
# Potentially also import from gen_rocks, gen_trees, gen_bridges if needed:
# from .gen_rocks import spawn_rocks
# from .gen_trees import spawn_trees_non_grass
# from .gen_bridges import connect_grass_regions_with_bridges

# Import the ID constants and the forward/reverse maps from scenery_defs
from scenery_defs import (
    RIVER_ID,
    GRASS_ID,
    SEMICOLON_FLOOR_ID,
    EMPTY_FLOOR_ID,
    DEBUG_DOT_ID,
    build_forward_map,
    build_reverse_map
)

# We import the entire debug module
import debug

# Build caches for converting (char, color) <-> definition_id
FORWARD_MAP = build_forward_map()
REVERSE_MAP = build_reverse_map()

def tile_to_definition_id(ch, cpair):
    """
    Convert a (char, color_pair) tile into a recognized definition_id
    by looking it up in REVERSE_MAP (from scenery_defs).
    Fallback to EMPTY_FLOOR_ID if unknown.
    """
    return REVERSE_MAP.get((ch, cpair), EMPTY_FLOOR_ID)

def definition_id_to_tile(def_id):
    """
    Convert a definition_id into (char, color_pair) using FORWARD_MAP (from scenery_defs).
    Fallback to ('.', 17) if unknown, just for safety.
    """
    return FORWARD_MAP.get(def_id, ('.', 17))

def generate_procedural_map(width=100, height=100):
    """
    Orchestrates procedural map generation by calling sub-generation modules:
      1) spawn_rivers -> sets tiles to (' ', 4) => "RIVER_ID"
      2) spawn_large_semicircle_grass -> sets tiles to (' ', 5) => "GRASS_ID"
      3) BFS from grass to fill blank with either SEMICOLON_FLOOR or EMPTY_FLOOR
      4) Overwrite empty floor tiles with DEBUG_DOT if debug is enabled.

    Returns a dict: {
      "world_width":  width,
      "world_height": height,
      "scenery": [ {x, y, definition_id}, ... ]
    }
    """

    # 1) Initialize a 2D grid of None => blank
    grid = [[None for _ in range(width)] for _ in range(height)]

    # 2) Rivers => sets some tiles to (' ', 4)
    spawn_rivers(grid, width, height, min_rivers=1, max_rivers=2)

    # 3) Create large grass patches => (' ', 5)
    spawn_large_semicircle_grass(
        grid,
        width,
        height,
        bundles=20,
        patch_size=60
    )

    # BFS data
    distance_map = [[99999]*width for _ in range(height)]
    queue = deque()

    # Identify grass => BFS starting points
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None:
                ch, cpair = grid[y][x]
                def_id = tile_to_definition_id(ch, cpair)
                if def_id == GRASS_ID:
                    distance_map[y][x] = 0
                    queue.append((x, y))

    # Multi-source BFS outward from grass
    while queue:
        cx, cy = queue.popleft()
        current_dist = distance_map[cy][cx]
        for nx, ny in [(cx+1,cy), (cx-1,cy), (cx,cy+1), (cx,cy-1)]:
            if 0 <= nx < width and 0 <= ny < height:
                if distance_map[ny][nx] > current_dist + 1:
                    distance_map[ny][nx] = current_dist + 1
                    queue.append((nx, ny))

    # Fill blank tiles with SEMICOLON_FLOOR or EMPTY_FLOOR
    for y in range(height):
        for x in range(width):
            if grid[y][x] is None:
                dist = distance_map[y][x]
                if dist <= 5:
                    # near grass => semicolon
                    grid[y][x] = definition_id_to_tile(SEMICOLON_FLOOR_ID)
                else:
                    # far from grass => empty
                    grid[y][x] = definition_id_to_tile(EMPTY_FLOOR_ID)

    # If debug enabled => transform empty floors to debug dots
    if debug.DEBUG_CONFIG["enabled"]:
        for y in range(height):
            for x in range(width):
                ch, cpair = grid[y][x]
                def_id = tile_to_definition_id(ch, cpair)
                if def_id == EMPTY_FLOOR_ID:
                    # override with debug dot
                    grid[y][x] = definition_id_to_tile(DEBUG_DOT_ID)

    # Convert grid => scenery list
    scenery_list = []
    for y in range(height):
        for x in range(width):
            ch, cpair = grid[y][x]
            def_id = tile_to_definition_id(ch, cpair)
            scenery_list.append({
                "x": x,
                "y": y,
                "definition_id": def_id
            })

    return {
        "world_width": width,
        "world_height": height,
        "scenery": scenery_list
    }