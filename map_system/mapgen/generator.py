# FileName: generator.py
# version: 2.5 (updated for multi-layer definitions, no local constants)
# Summary: Coordinates the procedural generation workflow, calling sub-generators 
#          (rivers, grass, trees, rocks, etc.) in order.
# Tags: map, generation, pipeline

import tools.debug as debug

# -------------------------------------------------------------------------
# 2) FEATURE TOGGLES
# -------------------------------------------------------------------------
ENABLE_RIVERS = True
ENABLE_GRASS  = True
ENABLE_TREES  = False
ENABLE_ROCKS  = False

# -------------------------------------------------------------------------
# 3) UTILITY IMPORTS
# -------------------------------------------------------------------------
from .gen_utils import compute_distance_map_bfs

# -------------------------------------------------------------------------
# 4) Import ALL_SCENERY_DEFS from scenery_manager for ID validation
# -------------------------------------------------------------------------
from scenery.scenery_manager import ALL_SCENERY_DEFS

# -------------------------------------------------------------------------
# 5) MAIN GENERATION FUNCTION
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

    # 2) Rivers => sets some tiles to "River"
    if ENABLE_RIVERS:
        spawn_rivers(grid, width, height, min_rivers=1, max_rivers=2)

    # 3) Grass => sets some tiles to "Grass"
    if ENABLE_GRASS:
        spawn_large_semicircle_grass(
            grid,
            width,
            height,
            bundles=20,
            patch_size=60
        )

    # Identify "Grass" tiles => BFS starting points
    grass_starts = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] == "Grass":
                grass_starts.append((x, y))

    # 4) Fill blank tiles (None) with "SemicolonFloor" or "EmptyFloor",
    #    depending on distance from grass.
    def passable_func(x, y):
        return True  # BFS can pass all squares

    distance_map = compute_distance_map_bfs(width, height, grass_starts, passable_func)

    for y in range(height):
        for x in range(width):
            if grid[y][x] is None:
                dist = distance_map[y][x]
                # near grass => "SemicolonFloor"
                if dist <= 5:
                    grid[y][x] = "SemicolonFloor"
                else:
                    grid[y][x] = "EmptyFloor"

    # Debug => turn "EmptyFloor" into "DebugDot" if debugging is on
    if debug.DEBUG_CONFIG["enabled"]:
        for y in range(height):
            for x in range(width):
                if grid[y][x] == "EmptyFloor":
                    grid[y][x] = "DebugDot"

    # 5) Optionally spawn trees in non-grass areas
    if ENABLE_TREES:
        spawn_trees_non_grass(grid, width, height, tree_min=5, tree_max=10)

    # 6) Optionally spawn rocks on grass
    if ENABLE_ROCKS:
        spawn_rocks(grid, width, height, rock_min=10, rock_max=20)

    # 7) Convert grid => a list of {"x", "y", "definition_id"} for each tile
    #    and ensure each def_id is recognized by ALL_SCENERY_DEFS. 
    #    If not, fallback to "EmptyFloor".
    scenery_list = []
    for y in range(height):
        for x in range(width):
            def_id = grid[y][x]
            if def_id not in ALL_SCENERY_DEFS:
                def_id = "EmptyFloor"
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

    # ---------------------------------------------------------------------
    # END of generate_procedural_map
    # ---------------------------------------------------------------------