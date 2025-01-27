# gen_grass.py
# Handles creation of grass patches, BFS for grass regions, and finding random grass spots.

import random

def spawn_grass_patches(grid, width, height, patch_count_min=3, patch_count_max=10):
    """
    Creates 3..10 separate grass patches, each ~10..20 tiles in size,
    typically placed near a water cell.
    """
    patch_count = random.randint(patch_count_min, patch_count_max)
    for _ in range(patch_count):
        create_grass_patch(grid, width, height, patch_size_min=10, patch_size_max=20)

def create_grass_patch(grid, width, height, patch_size_min=10, patch_size_max=20):
    """
    Creates one patch of grass (char=' ', color=5) near a random water tile,
    spreading BFS-like into ~10..20 cells.
    """
    water_positions = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None and grid[y][x][1] == 4:
                water_positions.append((x, y))
    if not water_positions:
        return  # no water found => skip

    # pick one water cell
    wx, wy = random.choice(water_positions)

    # find a neighbor cell that is None to start grass
    directions = [(0,1),(0,-1),(1,0),(-1,0)]
    random.shuffle(directions)
    start_cell = None
    for (dx, dy) in directions:
        nx, ny = wx + dx, wy + dy
        if 0 <= nx < width and 0 <= ny < height:
            if grid[ny][nx] is None:
                start_cell = (nx, ny)
                break
    if not start_cell:
        return

    patch_size = random.randint(patch_size_min, patch_size_max)
    queue = [start_cell]
    visited = set([start_cell])
    filled_count = 0

    while queue and filled_count < patch_size:
        cx, cy = queue.pop(0)
        if grid[cy][cx] is None:
            grid[cy][cx] = (' ', 5)  # grass
            filled_count += 1

        # expand neighbors
        random.shuffle(directions)
        for (dx, dy) in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited and grid[ny][nx] is None:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

def find_grass_regions(grid, width, height):
    """
    Uses BFS to identify distinct 'regions' of grass (char=' ', color=5).
    Returns a list of lists => each sublist is the set of coordinates for that region.
    """
    visited = [[False]*width for _ in range(height)]
    directions = [(0,1),(0,-1),(1,0),(-1,0)]
    regions = []

    for y in range(height):
        for x in range(width):
            if grid[y][x] is None:
                continue

            (ch, cpair) = grid[y][x]
            if ch == ' ' and cpair == 5 and not visited[y][x]:
                region_coords = []
                queue = [(x,y)]
                visited[y][x] = True

                while queue:
                    cx, cy = queue.pop(0)
                    region_coords.append((cx, cy))

                    for (dx, dy) in directions:
                        nx, ny = cx+dx, cy+dy
                        if 0 <= nx < width and 0 <= ny < height:
                            if not visited[ny][nx] and grid[ny][nx] is not None:
                                nch, ncp = grid[ny][nx]
                                if nch == ' ' and ncp == 5:
                                    visited[ny][nx] = True
                                    queue.append((nx, ny))
                regions.append(region_coords)

    return regions

def find_random_grass_spot(grid, width, height):
    """
    Return (x, y) of a random tile that is grass (char=' ', color=5).
    If none found, returns (0,0).
    """
    grass_positions = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None:
                (ch, cp) = grid[y][x]
                if ch == ' ' and cp == 5:
                    grass_positions.append((x, y))
    if not grass_positions:
        return (0, 0)
    return random.choice(grass_positions)
