# FileName: gen_grass.py
# version: 1.0
# Summary: Handles creation of grass patches, BFS for grass regions, etc.
# Tags: map, generation, grass

from .gen_utils import flood_fill_bfs
import random
import math

def spawn_large_semicircle_grass(grid, width, height, bundles=5, patch_size=40):
    """
    Creates 'bundles' of large grass areas. We store grass as (' ', 'white_on_green').
    """
    # find all water positions for reference
    water_positions = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None:
                ch, cpair = grid[y][x]
                # water => (ch=' ', color_name='white_on_blue')
                if ch == ' ' and cpair == 'white_on_blue':
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
                    grid[y][x] = (' ', 'white_on_green')  # grass
                    placed += 1

def find_grass_regions(grid, width, height):
    visited = [[False] * width for _ in range(height)]
    regions = []
    for y in range(height):
        for x in range(width):
            if not visited[y][x] and grid[y][x] is not None:
                ch, cp = grid[y][x]
                if ch == ' ' and cp == 'white_on_green':
                    region_coords = flood_fill_bfs(
                        width, height, x, y,
                        match_func=lambda nx, ny: (
                            grid[ny][nx] is not None and
                            grid[ny][nx][0] == ' ' and
                            grid[ny][nx][1] == 'white_on_green'
                        )
                    )
                    for (rx, ry) in region_coords:
                        visited[ry][rx] = True
                    regions.append(region_coords)
    return regions



#def find_random_grass_spot(grid, width, height):
#    """
#    Return (x, y) of a random tile that is grass.
#    If none found, returns (0, 0).
#    """
#    grass_positions = []
#    for y in range(height):
#        for x in range(width):
#            if grid[y][x] is not None:
#                ch, cp = grid[y][x]
#                if ch == ' ' and cp == 'white_on_green':
#                    grass_positions.append((x, y))
#    if not grass_positions:
#        return (0, 0)
#    return random.choice(grass_positions)