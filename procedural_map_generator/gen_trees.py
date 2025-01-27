# gen_trees.py
# Spawns trees on non-grass tiles, at least 2 tiles from grass and 1 tile away from each other.

import random
from .utils import manhattan_dist

def spawn_trees_non_grass(grid, width, height, tree_min=5, tree_max=10):
    """
    Place trees (trunk '|', color=2, plus top '§', color=1) on tiles that are:
      - not grass
      - at least 2 tiles away from any grass
      - at least 1 tile away from other trees
    """
    grass_positions = []
    # Collect all grass coords
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None:
                ch, cpair = grid[y][x]
                if ch == ' ' and cpair == 5:
                    grass_positions.append((x, y))

    # Build a list of valid non-grass positions (>=2 away from grass)
    valid_positions = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None:
                (ch, cpair) = grid[y][x]
                # only consider if NOT grass
                if not (ch == ' ' and cpair == 5):
                    dist_ok = True
                    for (gx, gy) in grass_positions:
                        if manhattan_dist(x, y, gx, gy) < 2:
                            dist_ok = False
                            break
                    if dist_ok:
                        valid_positions.append((x, y))

    placed_trees = []
    count = random.randint(tree_min, tree_max)

    for _ in range(count):
        if not valid_positions:
            break
        tx, ty = random.choice(valid_positions)

        # We need space above for the top
        if ty > 0:
            # top cell is (tx, ty-1)
            if (tx, ty-1) in valid_positions:
                # also check adjacency to existing trunks
                too_close = any(manhattan_dist(tx, ty, px, py) <= 1 for (px, py) in placed_trees)
                if not too_close:
                    # place the tree
                    grid[ty][tx] = ('|', 2)   # trunk
                    grid[ty-1][tx] = ('§', 1) # top
                    placed_trees.append((tx, ty))

                    # remove trunk + top from valid_positions
                    valid_positions.remove((tx, ty))
                    valid_positions.remove((tx, ty-1))

                    # also remove anything else too close
                    purge_positions_close(valid_positions, tx, ty, 1)
                    purge_positions_close(valid_positions, tx, ty-1, 1)

def purge_positions_close(pos_list, cx, cy, radius=1):
    """
    Remove from pos_list any positions that are within 'radius' manhattan distance to (cx, cy).
    """
    removals = []
    for (vx, vy) in pos_list:
        if manhattan_dist(vx, vy, cx, cy) <= radius:
            removals.append((vx, vy))
    for r in removals:
        pos_list.remove(r)
