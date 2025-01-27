# FileName: generator.py
# version: 1.9 (Now uses constants from scenery_main instead of raw color checks)

import random
from collections import deque  # for BFS queue

# Import all generation functions
from .gen_scenery import (
    spawn_rivers,
    spawn_large_semicircle_grass,
    spawn_rocks,
    spawn_trees_non_grass,
    connect_grass_regions_with_bridges,
    find_grass_regions,
    find_random_grass_spot
)

# Import the ID constants and the forward/reverse maps
from scenery_main import (
    RIVER_ID,
    GRASS_ID,
    SEMICOLON_FLOOR_ID,
    EMPTY_FLOOR_ID,
    DEBUG_DOT_ID,
    build_forward_map,
    build_reverse_map
)

# [CHANGED] Import the entire debug module, not just the variable
import debug

# Build caches for converting (char, color) <-> definition_id
FORWARD_MAP = build_forward_map()
REVERSE_MAP = build_reverse_map()

def tile_to_definition_id(ch, cpair):
    """
    Convert a (char, color_pair) tile into a recognized definition_id
    by looking it up in scenery_main's reverse map.
    Fallback to EMPTY_FLOOR_ID if unknown.
    """
    return REVERSE_MAP.get((ch, cpair), EMPTY_FLOOR_ID)

def definition_id_to_tile(def_id):
    """
    Convert a definition_id into (char, color_pair) using scenery_main's forward map.
    Fallback to ('.', 17) if unknown (just for safety).
    """
    return FORWARD_MAP.get(def_id, ('.', 17))

def generate_procedural_map(width=100, height=100):
    """
    Orchestrates procedural map generation by calling gen_* modules:
      1) spawn_rivers (sets tiles to (' ', 4) => "River")
      2) spawn_large_semicircle_grass (sets tiles to (' ', 5) => "Grass")
      3) BFS from grass to fill blank with either SemicolonFloor or EmptyFloor
      4) (Optional) Overwrite empty floor tiles with DebugDot if debug is enabled.

    Returns:
      {
        "world_width":  width,
        "world_height": height,
        "scenery": [
          {"x": x, "y": y, "definition_id": ...},
          ...
        ]
      }
    """
    # 1) Initialize a 2D grid with None => blank
    grid = [[None for _ in range(width)] for _ in range(height)]

    # 2) Spawn rivers => sets some tiles to (' ', 4)
    spawn_rivers(grid, width, height, min_rivers=1, max_rivers=2)

    # 3) Create large grass patches => (' ', 5)
    spawn_large_semicircle_grass(
        grid,
        width,
        height,
        bundles=20,   # how many lumps
        patch_size=60 # how many tiles per lump
    )

    # (Optional) Additional features if you like:
    # spawn_rocks(grid, width, height, rock_min=10, rock_max=20)
    # spawn_trees_non_grass(grid, width, height, tree_min=5, tree_max=10)
    # connect_grass_regions_with_bridges(grid, ...)

    # Prepare BFS from all grass tiles
    distance_map = [[99999] * width for _ in range(height)]
    queue = deque()

    # Identify Grass => BFS start points
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
        for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
            if 0 <= nx < width and 0 <= ny < height:
                if distance_map[ny][nx] > current_dist + 1:
                    distance_map[ny][nx] = current_dist + 1
                    queue.append((nx, ny))

    # Fill blank tiles with either SemicolonFloor or EmptyFloor
    for y in range(height):
        for x in range(width):
            if grid[y][x] is None:
                dist = distance_map[y][x]
                if dist <= 5:
                    # near grass => semicolon
                    grid[y][x] = definition_id_to_tile(SEMICOLON_FLOOR_ID)
                else:
                    # far from grass => empty space
                    grid[y][x] = definition_id_to_tile(EMPTY_FLOOR_ID)

    # -------------------------------------------------------------
    # 4) FINAL DEBUG PASS: only if debug.DEBUG_ENABLED == True
    # -------------------------------------------------------------
    if debug.DEBUG_CONFIG["enabled"]:
        for y in range(height):
            for x in range(width):
                ch, cpair = grid[y][x]
                def_id = tile_to_definition_id(ch, cpair)
                if def_id == EMPTY_FLOOR_ID:
                    grid[y][x] = definition_id_to_tile(DEBUG_DOT_ID)

    # Convert grid => scenery list
    scenery_list = []
    for y in range(height):
        for x in range(width):
            ch, cpair = grid[y][x]
            # Convert tile -> definition_id
            def_id = tile_to_definition_id(ch, cpair)
            scenery_list.append({
                "x": x,
                "y": y,
                "definition_id": def_id
            })

    # Return final map data
    return {
        "world_width": width,
        "world_height": height,
        "scenery": scenery_list
    }