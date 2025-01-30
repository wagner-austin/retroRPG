# gen_rocks.py
# version: 1.0
# Summary: Spawns rocks on existing grass tiles, if used.
# Tags: map, generation, rocks

import random
from .gen_grass import find_random_grass_spot

def spawn_rocks(grid, width, height, rock_min=10, rock_max=20):
    """
    Randomly place 10..20 rocks on grass.
    We'll store a rock as ('o', 'white_on_black').
    """
    count = random.randint(rock_min, rock_max)
    for _ in range(count):
        gx, gy = find_random_grass_spot(grid, width, height)
        cluster_size = random.randint(1, 3)
        for _c in range(cluster_size):
            rx = gx + random.randint(-1, 1)
            ry = gy + random.randint(-1, 1)
            if 0 <= rx < width and 0 <= ry < height:
                if grid[ry][rx] is not None:
                    ch, cp = grid[ry][rx]
                    # Grass => (' ', 'white_on_green')
                    if ch == ' ' and cp == 'white_on_green':
                        grid[ry][rx] = ('o', 'white_on_black')