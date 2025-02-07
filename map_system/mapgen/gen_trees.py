# FileName: gen_trees.py
# version: 1.2 (no longer uses generator.py constants)
# Summary: Spawns trees on non-grass tiles, checking adjacency.
# Tags: map, generation, trees

import random
from .gen_utils import manhattan_dist

# -------------------------------------------------------------------------
# OLD IMPORTS (commented out)
# from .generator import GRASS_ID, TREE_TRUNK_ID, TREE_TOP_ID
#
# We no longer import these constants from generator.py;
# we instead use literal strings "Grass", "TreeTrunk", "TreeTop".
# -------------------------------------------------------------------------

def spawn_trees_non_grass(grid, width, height, tree_min=5, tree_max=10):
    """
    Places trees on tiles that are NOT "Grass", at least 2 away from grass.
    We store trunk as "TreeTrunk" and top as "TreeTop".
    """

    # 1) Identify all grass positions
    grass_positions = []
    for y in range(height):
        for x in range(width):
            # if grid[y][x] == GRASS_ID:
            if grid[y][x] == "Grass":
                grass_positions.append((x, y))

    # 2) Build a list of valid positions that are not grass
    #    and at least 2 away from any grass tile
    valid_positions = []
    for y in range(height):
        for x in range(width):
            tile_id = grid[y][x]
            # if tile_id is not None and tile_id != GRASS_ID:
            if tile_id is not None and tile_id != "Grass":
                dist_ok = True
                for (gx, gy) in grass_positions:
                    if manhattan_dist(x, y, gx, gy) < 2:
                        dist_ok = False
                        break
                if dist_ok:
                    valid_positions.append((x, y))

    # 3) Randomly choose positions to place trees
    placed_trees = []
    count = random.randint(tree_min, tree_max)
    for _ in range(count):
        if not valid_positions:
            break
        tx, ty = random.choice(valid_positions)

        # We place trunk at (tx, ty) and top at (tx, ty-1) if possible
        if ty > 0 and (tx, ty - 1) in valid_positions:
            too_close = any(manhattan_dist(tx, ty, px, py) <= 1 for (px, py) in placed_trees)
            if not too_close:
                # grid[ty][tx] = TREE_TRUNK_ID
                # grid[ty - 1][tx] = TREE_TOP_ID
                grid[ty][tx] = "TreeTrunk"
                grid[ty - 1][tx] = "TreeTop"
                placed_trees.append((tx, ty))

                # Remove these tiles from valid_positions
                valid_positions.remove((tx, ty))
                valid_positions.remove((tx, ty - 1))

                # Purge positions close to trunk or top so we don't overlap
                purge_positions_close(valid_positions, tx, ty, 1)
                purge_positions_close(valid_positions, tx, ty - 1, 1)


def purge_positions_close(pos_list, cx, cy, radius=1):
    """
    Removes positions from pos_list that are within 'radius' distance
    of (cx, cy), using manhattan_dist.
    """
    removals = []
    for (vx, vy) in pos_list:
        if manhattan_dist(vx, vy, cx, cy) <= radius:
            removals.append((vx, vy))
    for r in removals:
        pos_list.remove(r)