# gen_trees.py
# version: 1.0
# Summary: Spawns trees on non-grass tiles, checking adjacency.
# Tags: map, generation, trees

import random
from .utils import manhattan_dist

def spawn_trees_non_grass(grid, width, height, tree_min=5, tree_max=10):
    """
    Place trunk => ('|', 'yellow_on_black'), top => ('§', 'green_on_black')
    on tiles that are not grass, at least 2 away from grass, etc.
    """
    grass_positions = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None:
                ch, cpair = grid[y][x]
                if ch == ' ' and cpair == 'white_on_green':
                    grass_positions.append((x, y))

    valid_positions = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None:
                (ch, cpair) = grid[y][x]
                if not (ch == ' ' and cpair == 'white_on_green'):
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
        if ty > 0:
            if (tx, ty - 1) in valid_positions:
                too_close = any(manhattan_dist(tx, ty, px, py) <= 1 for (px, py) in placed_trees)
                if not too_close:
                    grid[ty][tx] = ('|', 'yellow_on_black')  # trunk
                    grid[ty - 1][tx] = ('§', 'green_on_black')  # top
                    placed_trees.append((tx, ty))
                    valid_positions.remove((tx, ty))
                    valid_positions.remove((tx, ty - 1))
                    purge_positions_close(valid_positions, tx, ty, 1)
                    purge_positions_close(valid_positions, tx, ty - 1, 1)

def purge_positions_close(pos_list, cx, cy, radius=1):
    removals = []
    for (vx, vy) in pos_list:
        if manhattan_dist(vx, vy, cx, cy) <= radius:
            removals.append((vx, vy))
    for r in removals:
        pos_list.remove(r)