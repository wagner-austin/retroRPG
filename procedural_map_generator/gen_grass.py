# gen_grass.py
# Handles creation of grass patches, BFS for grass regions, and finding random grass spots.

import random
import math  # ADDED: for spawn_large_semicircle_grass (sqrt, sin, cos, etc.)

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

def spawn_large_semicircle_grass(grid, width, height,
                                 bundles=5, patch_size=40):
    """
    Creates 'bundles' of large grass areas near the river.
    Each bundle picks a random river tile and forms a rough semi-circle
    of 'patch_size' tiles outward from that point.

    - We pick a center angle, then scatter grass within +/-90 degrees from it,
      up to some random radius, to emulate a semi-circular region.
    - 'bundles' => how many lumps
    - 'patch_size' => how many tiles in each lump
    - The tile for grass is (' ', 5).

    Updated for larger coverage:
      - radius is bigger => +8 instead of +4
    """
    # Gather all river (water) positions
    water_positions = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None:
                ch, cpair = grid[y][x]
                # water => (' ', 4)
                if ch == ' ' and cpair == 4:
                    water_positions.append((x, y))

    if not water_positions:
        return  # No rivers => skip

    for _ in range(bundles):
        # Pick a random water tile as "center"
        center_x, center_y = random.choice(water_positions)

        # Random "orientation" for the semicircle
        center_angle = random.uniform(0, 360)

        # We'll define a rough radius for the lumps.
        radius = int(math.sqrt(patch_size)) + 8

        placed = 0
        attempts = 0
        max_attempts = patch_size * 10

        while placed < patch_size and attempts < max_attempts:
            attempts += 1

            # Random angle within +/- 90 deg from center_angle
            angle_offset = random.uniform(-90, 90)
            angle = math.radians(center_angle + angle_offset)

            # Random distance from [0..radius]
            r = random.uniform(0, radius)

            # Compute potential coords
            dx = int(round(r * math.cos(angle)))
            dy = int(round(r * math.sin(angle)))
            x = center_x + dx
            y = center_y + dy

            if 0 <= x < width and 0 <= y < height:
                # Place grass if None
                if grid[y][x] is None:
                    grid[y][x] = (' ', 5)  # grass
                    placed += 1

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
    If none found, returns (0, 0).
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