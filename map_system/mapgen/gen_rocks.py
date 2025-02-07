# FileName: gen_rocks.py
# version: 1.2 (no longer uses generator.py constants)
# Summary: Spawns rocks on existing grass tiles, if used.
# Tags: map, generation, rocks

import random

# OLD IMPORTS (commented out):
# from .generator import ROCK_ID, GRASS_ID
# from .gen_grass import find_random_grass_spot

# We replace with literal strings "Rock", "Grass".
# We still use find_random_grass_spot to get a (gx, gy).

from .gen_grass import find_random_grass_spot

def spawn_rocks(grid, width, height, rock_min=10, rock_max=20):
    """
    Randomly place 10..20 rocks on grass. We store rocks as "Rock".
    """

    count = random.randint(rock_min, rock_max)
    for _ in range(count):
        gx, gy = find_random_grass_spot(grid, width, height)
        cluster_size = random.randint(1, 3)
        for _c in range(cluster_size):
            rx = gx + random.randint(-1, 1)
            ry = gy + random.randint(-1, 1)
            if 0 <= rx < width and 0 <= ry < height:
                tile_id = grid[ry][rx]
                # if tile_id == GRASS_ID:
                if tile_id == "Grass":
                    # grid[ry][rx] = ROCK_ID
                    grid[ry][rx] = "Rock"