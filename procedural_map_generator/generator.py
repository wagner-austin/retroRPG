# FileName: generator.py
# version: 2.4
# Summary: Coordinates the procedural generation workflow, calling sub-generators 
#          (rivers, grass, trees, rocks, etc.) in order.
# Tags: map, generation, pipeline

import random
import debug

# -------------------------------------------------------------------------
# 1) SINGLE SOURCE OF TRUTH FOR DEFINITION ID CONSTANTS
# -------------------------------------------------------------------------
RIVER_ID            = "River"
GRASS_ID            = "Grass"
SEMICOLON_FLOOR_ID  = "SemicolonFloor"
EMPTY_FLOOR_ID      = "EmptyFloor"
DEBUG_DOT_ID        = "DebugDot"
TREE_TRUNK_ID       = "TreeTrunk"
TREE_TOP_ID         = "TreeTop"
ROCK_ID             = "Rock"

# -------------------------------------------------------------------------
# 2) FEATURE TOGGLES
# -------------------------------------------------------------------------
ENABLE_RIVERS = True
ENABLE_GRASS  = True
ENABLE_TREES  = False
ENABLE_ROCKS  = False

# -------------------------------------------------------------------------
# 3) UTILITY IMPORTS
#     - We import 'compute_distance_map_bfs' from gen_utils at top level,
#       since it should not import anything from generator.py, avoiding cycles.
# -------------------------------------------------------------------------
from .gen_utils import compute_distance_map_bfs

# -------------------------------------------------------------------------
# 4) MAIN GENERATION FUNCTION
#     - We do a LAZY import of sub-generators inside the function to avoid
#       circular references, so they can import our constants.
# -------------------------------------------------------------------------
def generate_procedural_map(width=100, height=100):
    """
    Orchestrates procedural map generation, storing definition IDs directly in grid[y][x].
    At the end, we build a list of scenery dicts.

    Feature toggles:
        ENABLE_RIVERS, ENABLE_GRASS, ENABLE_TREES, ENABLE_ROCKS
    """

    # Avoid circular imports by importing sub-generators here:
    from .gen_rivers import spawn_rivers
    from .gen_grass import spawn_large_semicircle_grass
    from .gen_trees import spawn_trees_non_grass
    from .gen_rocks import spawn_rocks

    # 1) Initialize a 2D grid of None => blank
    grid = [[None for _ in range(width)] for _ in range(height)]

    # 2) Rivers => sets some tiles to RIVER_ID
    if ENABLE_RIVERS:
        spawn_rivers(grid, width, height, min_rivers=1, max_rivers=2)

    # 3) Grass => sets some tiles to GRASS_ID
    if ENABLE_GRASS:
        spawn_large_semicircle_grass(
            grid,
            width,
            height,
            bundles=20,
            patch_size=60
        )

    # Identify Grass tiles => BFS starting points
    grass_starts = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] == GRASS_ID:
                grass_starts.append((x, y))

    # 4) Fill blank tiles (None) with SEMICOLON_FLOOR_ID or EMPTY_FLOOR_ID,
    #    depending on distance from grass.
    def passable_func(x, y):
        return True  # no blocking for BFS fill

    distance_map = compute_distance_map_bfs(width, height, grass_starts, passable_func)

    for y in range(height):
        for x in range(width):
            if grid[y][x] is None:
                dist = distance_map[y][x]
                # near grass => semicolon floor
                if dist <= 5:
                    grid[y][x] = SEMICOLON_FLOOR_ID
                else:
                    grid[y][x] = EMPTY_FLOOR_ID

    # Debug => turn empty floors into debug dots
    if debug.DEBUG_CONFIG["enabled"]:
        for y in range(height):
            for x in range(width):
                if grid[y][x] == EMPTY_FLOOR_ID:
                    grid[y][x] = DEBUG_DOT_ID

    # 5) Optionally spawn trees in non-grass areas
    if ENABLE_TREES:
        spawn_trees_non_grass(grid, width, height, tree_min=5, tree_max=10)

    # 6) Optionally spawn rocks on grass
    if ENABLE_ROCKS:
        spawn_rocks(grid, width, height, rock_min=10, rock_max=20)

    # Convert grid => scenery list
    scenery_list = []
    for y in range(height):
        for x in range(width):
            def_id = grid[y][x]
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