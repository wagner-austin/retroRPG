# FileName: gen_grass.py
# version: 1.2 (no longer uses generator.py constants)
# Summary: Handles creation of grass patches, BFS for grass regions, etc.
# Tags: map, generation, grass

import random
import math

# OLD IMPORTS (commented out):
# from .generator import GRASS_ID, RIVER_ID
# from .gen_utils import flood_fill_bfs
#
# We still import flood_fill_bfs, but we use literal "Grass" and "River".

from .gen_utils import flood_fill_bfs

def spawn_large_semicircle_grass(grid, width, height, bundles=5, patch_size=40):
    """
    Creates 'bundles' of large grass areas. We store grass as "Grass".
    """
    # find all "River" positions
    water_positions = []
    for y in range(height):
        for x in range(width):
            # if grid[y][x] == RIVER_ID:
            if grid[y][x] == "River":
                water_positions.append((x, y))

    if not water_positions:
        return

    for _ in range(bundles):
        center_x, center_y = random.choice(water_positions)
        center_angle = random.uniform(0, 360)
        radius = int(math.sqrt(patch_size)) + 8

        placed = 0
        attempts = 0
        max_attempts = patch_size * 10

        while placed < patch_size and attempts < max_attempts:
            attempts += 1
            angle_offset = random.uniform(-90, 90)
            angle = math.radians(center_angle + angle_offset)
            r = random.uniform(0, radius)
            dx = int(round(r * math.cos(angle)))
            dy = int(round(r * math.sin(angle)))
            x = center_x + dx
            y = center_y + dy

            if 0 <= x < width and 0 <= y < height:
                if grid[y][x] is None:
                    # grid[y][x] = GRASS_ID
                    grid[y][x] = "Grass"
                    placed += 1

def find_grass_regions(grid, width, height):
    """
    Returns a list of contiguous BFS regions for tiles labeled "Grass".
    Each region is a list of (x, y) coords.
    """
    visited = [[False] * width for _ in range(height)]
    regions = []
    for y in range(height):
        for x in range(width):
            # if grid[y][x] == GRASS_ID and not visited[y][x]:
            if grid[y][x] == "Grass" and not visited[y][x]:
                region_coords = flood_fill_bfs(
                    width, height, x, y,
                    match_func=lambda nx, ny: (grid[ny][nx] == "Grass")
                )
                for (rx, ry) in region_coords:
                    visited[ry][rx] = True
                regions.append(region_coords)
    return regions

def find_random_grass_spot(grid, width, height):
    """
    Return (x, y) of a random tile that is "Grass".
    If none found, returns (0, 0).
    """
    grass_positions = []
    for y in range(height):
        for x in range(width):
            # if grid[y][x] == GRASS_ID:
            if grid[y][x] == "Grass":
                grass_positions.append((x, y))
    if not grass_positions:
        return (0, 0)
    return random.choice(grass_positions)