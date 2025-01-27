# gen_rocks.py
# Spawns rocks on existing grass tiles.

import random
from .gen_grass import find_random_grass_spot

def spawn_rocks(grid, width, height, rock_min=10, rock_max=20):
    """
    Randomly place 10..20 rocks (char='o', color=3) on grass.
    Each "group" is size 1..3, for a clustered feel.
    """
    count = random.randint(rock_min, rock_max)
    for _ in range(count):
        gx, gy = find_random_grass_spot(grid, width, height)
        # cluster size 1..3
        cluster_size = random.randint(1, 3)
        for _c in range(cluster_size):
            rx = gx + random.randint(-1,1)
            ry = gy + random.randint(-1,1)
            if 0 <= rx < width and 0 <= ry < height:
                if grid[ry][rx] is not None:
                    ch, cp = grid[ry][rx]
                    if ch == ' ' and cp == 5:  # grass
                        grid[ry][rx] = ('o', 3)
