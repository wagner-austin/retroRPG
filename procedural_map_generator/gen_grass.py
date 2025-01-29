# FileName: gen_grass.py
# version: 1.0
# Summary: Handles creation of grass patches, BFS for grass regions, etc.
# Tags: map, generation, grass

import random
import math
from .utils import manhattan_dist, flood_fill_bfs

def spawn_large_semicircle_grass(grid, width, height,
                                 bundles=5, patch_size=40):
    """
    Creates 'bundles' of large grass areas near water. Each bundle picks
    a random river tile as center, forms a rough semi-circle of 'patch_size'.
    Grass tile => (' ', 5).
    """
    # find all water positions
    water_positions = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None:
                ch, cp = grid[y][x]
                # water => (ch=' ', cp=4)
                if ch == ' ' and cp == 4:
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
                    grid[y][x] = (' ', 5)  # grass
                    placed += 1


def find_grass_regions(grid, width, height):
    """
    Uses a BFS approach to identify distinct 'regions' of grass (ch=' ', cpair=5).
    We rely on flood_fill_bfs from our utils.
    """
    visited = [[False] * width for _ in range(height)]
    regions = []

    for y in range(height):
        for x in range(width):
            if not visited[y][x] and grid[y][x] is not None:
                ch, cp = grid[y][x]
                if ch == ' ' and cp == 5:
                    region_coords = flood_fill_bfs(
                        width, height, x, y,
                        match_func=lambda nx, ny: (
                            grid[ny][nx] is not None and
                            grid[ny][nx][0] == ' ' and
                            grid[ny][nx][1] == 5
                        )
                    )
                    for (rx, ry) in region_coords:
                        visited[ry][rx] = True
                    regions.append(region_coords)
    return regions


def find_random_grass_spot(grid, width, height):
    """
    Return (x, y) of a random tile that is grass (ch=' ', cpair=5).
    If none found, returns (0, 0).
    """
    grass_positions = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None:
                ch, cp = grid[y][x]
                if ch == ' ' and cp == 5:
                    grass_positions.append((x, y))
    if not grass_positions:
        return (0, 0)
    return random.choice(grass_positions)