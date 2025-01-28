# FileName: gen_scenery.py
# version: 1.0
# Summary: Consolidates all logic for placing procedural scenery: rivers, grass, rocks, trees, bridges, etc.
# Tags: map, generation, scenery

import random
import math  # For our semi-circle angle calculations

############################################
# UTILITY FUNCTION(S)
############################################

def manhattan_dist(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

############################################
# RIVER SPAWNING
############################################

def spawn_rivers(grid, width, height, min_rivers=1, max_rivers=2):
    """
    Spawns a certain number of rivers (default 1-2).
    Each river starts on one edge, ends on the opposite edge,
    follows a path that mixes straight and diagonal movements,
    and alternates between 3-wide and 1-wide sections.
    """
    river_count = random.randint(min_rivers, max_rivers)
    for _ in range(river_count):
        start, end = pick_opposite_edges(width, height)
        path = trace_river_path_improved(start, end, width, height)
        fill_river_alternate_widths(grid, path, width, height)

def pick_opposite_edges(width, height):
    """
    Pick one edge of the map at random (top, bottom, left, right),
    then pick the opposite edge, and return (start, end) positions.
    """
    # 0 = top->bottom, 1 = bottom->top, 2 = left->right, 3 = right->left
    edge_type = random.randint(0, 3)

    if edge_type == 0:
        # top -> bottom
        sx = random.randint(0, width - 1)
        sy = 0
        ex = random.randint(0, width - 1)
        ey = height - 1
    elif edge_type == 1:
        # bottom -> top
        sx = random.randint(0, width - 1)
        sy = height - 1
        ex = random.randint(0, width - 1)
        ey = 0
    elif edge_type == 2:
        # left -> right
        sx = 0
        sy = random.randint(0, height - 1)
        ex = width - 1
        ey = random.randint(0, height - 1)
    else:
        # right -> left
        sx = width - 1
        sy = random.randint(0, height - 1)
        ex = 0
        ey = random.randint(0, height - 1)

    return (sx, sy), (ex, ey)

def trace_river_path_improved(start, end, width, height):
    """
    Generates a path from start->end with segments that may be:
      - Straight moves
      - Diagonal "over-over-down" or "down-over-over" patterns
    We'll keep going until we reach or are very close to end.
    """
    (sx, sy) = start
    (ex, ey) = end
    path = []
    curx, cury = sx, sy
    path.append((curx, cury))

    # A loose bound to prevent infinite loops
    max_steps = (abs(ex - sx) + abs(ey - sy)) * 3

    for _ in range(max_steps):
        if (curx, cury) == (ex, ey):
            break

        dx = ex - curx
        dy = ey - cury

        # If very close, just jump
        if abs(dx) <= 1 and abs(dy) <= 1:
            curx, cury = ex, ey
            path.append((curx, cury))
            break

        # 30% chance for diagonal movement (if dx != 0 and dy != 0)
        do_diagonal = (random.random() < 0.3 and dx != 0 and dy != 0)

        if do_diagonal:
            # "over-over-down" or "down-over-over"
            sxn = 1 if dx > 0 else -1
            syn = 1 if dy > 0 else -1
            pattern_type = random.choice([0, 1])
            if pattern_type == 0:
                steps = [(sxn, 0), (sxn, 0), (0, syn)]
            else:
                steps = [(0, syn), (sxn, 0), (sxn, 0)]
        else:
            # Straight movement
            if abs(dx) > abs(dy):
                sxn = 1 if dx > 0 else -1
                steps = [(sxn, 0)] * random.randint(1, 2)
            else:
                syn = 1 if dy > 0 else -1
                steps = [(0, syn)] * random.randint(1, 2)

        # Apply steps
        for (mx, my) in steps:
            if (curx, cury) == (ex, ey):
                break
            curx += mx
            cury += my
            # Clamp
            curx = max(0, min(curx, width - 1))
            cury = max(0, min(cury, height - 1))
            path.append((curx, cury))
            if (curx, cury) == (ex, ey):
                break

    # Ensure end in path
    if (curx, cury) != (ex, ey):
        path.append((ex, ey))

    return path

def fill_river_alternate_widths(grid, path, width, height):
    """
    Every even index => fill center + neighbors (3-wide).
    Every odd index => fill center tile (1-wide).
    We'll use water = (' ', 4).
    """
    wide_offsets = [
        (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    for i, (x, y) in enumerate(path):
        if i % 2 == 0:
            # 3-wide
            for (ox, oy) in wide_offsets:
                nx = x + ox
                ny = y + oy
                if 0 <= nx < width and 0 <= ny < height:
                    grid[ny][nx] = (' ', 4)  # water
        else:
            # 1-wide
            grid[y][x] = (' ', 4)

############################################
# GRASS: LARGE SEMI-CIRCLES NEAR RIVERS
############################################

def spawn_large_semicircle_grass(grid, width, height,
                                 bundles=5, patch_size=40):
    """
    Creates 'bundles' of large grass areas near the river.
    Each bundle picks a random river tile and forms a rough semi-circle
    of 'patch_size' tiles outward from that point.

    - We pick a center angle, then scatter grass within +/-90 degrees from it,
      up to some small radius, to emulate a semi-circular region.
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
        # Larger base offset => more coverage
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

############################################
# FINDING GRASS REGIONS / RANDOM SPOT
############################################

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

############################################
# TREES (ON NON-GRASS)
############################################

def spawn_trees_non_grass(grid, width, height, tree_min=5, tree_max=10):
    """
    Place trees (2-tile: trunk + top) on tiles that are:
      - not grass
      - at least 2 tiles away from any grass
      - at least 1 tile away from other trees
    """
    grass_positions = []
    # Collect all grass coords
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None:
                ch, cpair = grid[y][x]
                if ch == ' ' and cpair == 5:
                    grass_positions.append((x, y))

    # Valid non-grass positions (>=2 away from grass)
    valid_positions = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] is not None:
                ch, cpair = grid[y][x]
                # Only consider if NOT grass
                if not (ch == ' ' and cpair == 5):
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

        # We need space above for the top
        if ty > 0:
            # Check adjacency to existing trunks
            too_close = any(manhattan_dist(tx, ty, px, py) <= 1 for (px, py) in placed_trees)
            if not too_close:
                # Place trunk + top
                grid[ty][tx] = ('|', 2)    # trunk
                grid[ty-1][tx] = ('§', 1)  # top
                placed_trees.append((tx, ty))

                # Remove trunk + top from valid_positions
                valid_positions.remove((tx, ty))
                if (tx, ty-1) in valid_positions:
                    valid_positions.remove((tx, ty-1))

                # Also remove anything else too close
                purge_positions_close(valid_positions, tx, ty, 1)
                purge_positions_close(valid_positions, tx, ty-1, 1)

def purge_positions_close(pos_list, cx, cy, radius=1):
    """
    Remove from pos_list any positions that are within 'radius' manhattan distance to (cx, cy).
    """
    removals = []
    for (vx, vy) in pos_list:
        if manhattan_dist(vx, vy, cx, cy) <= radius:
            removals.append((vx, vy))
    for r in removals:
        pos_list.remove(r)

############################################
# ROCKS (ON GRASS)
############################################

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

############################################
# BRIDGES BETWEEN GRASS REGIONS
############################################

def connect_grass_regions_with_bridges(grid, grass_regions):
    """
    Placeholder for custom bridging logic if you want to connect
    separate grass regions with some form of bridging tiles.
    """
    pass