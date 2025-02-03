# FileName: gen_rocks.py
# version: 1.1
# Summary: Spawns rocks on existing grass tiles, if used.
# Tags: map, generation, rocks

import random

# Import definition IDs from generator.py
from .generator import ROCK_ID, GRASS_ID
from .gen_grass import find_random_grass_spot

def spawn_rocks(grid, width, height, rock_min=10, rock_max=20):
    """
    Randomly place 10..20 rocks on grass. We store rocks as ROCK_ID.
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
                # Only place a rock if tile_id is GRASS_ID
                if tile_id == GRASS_ID:
                    grid[ry][rx] = ROCK_ID