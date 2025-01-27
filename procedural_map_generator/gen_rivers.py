# gen_rivers.py
# Handles river spawning, from choosing edge points to thickening the water path.

import random

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
    For instance, if we pick "top," the opposite is "bottom."
    """
    # 0 = top->bottom, 1 = bottom->top,
    # 2 = left->right, 3 = right->left
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

        # If we're very close to the end, just jump there
        if abs(dx) <= 1 and abs(dy) <= 1:
            curx, cury = ex, ey
            path.append((curx, cury))
            break

        # Decide randomly whether to do a diagonal pattern or a straight move
        # (e.g. 30% chance to attempt a diagonal movement, otherwise straight).
        do_diagonal = (random.random() < 0.3 and dx != 0 and dy != 0)

        if do_diagonal:
            # "over-over-down" or "down-over-over"
            # Convert dx, dy to -1, 0, or 1 sign
            sxn = 1 if dx > 0 else -1
            syn = 1 if dy > 0 else -1

            # Randomly choose which pattern to do
            pattern_type = random.choice([0, 1])
            if pattern_type == 0:
                # over, over, down
                steps = [(sxn, 0), (sxn, 0), (0, syn)]
            else:
                # down, over, over
                steps = [(0, syn), (sxn, 0), (sxn, 0)]
        else:
            # Straight movement (horizontal or vertical).
            # Decide horizontal vs vertical by whichever is larger in magnitude.
            if abs(dx) > abs(dy):
                # Move horizontally up to 2 steps
                sxn = 1 if dx > 0 else -1
                steps = [(sxn, 0)] * random.randint(1, 2)
            else:
                # Move vertically up to 2 steps
                syn = 1 if dy > 0 else -1
                steps = [(0, syn)] * random.randint(1, 2)

        # Apply the steps in the chosen pattern
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

    # Ensure the end is in the path
    if (curx, cury) != (ex, ey):
        path.append((ex, ey))

    return path

def fill_river_alternate_widths(grid, path, width, height):
    """
    For each index i in the path, if i is even => fill the tile + an extra
    'radius' around it (3-wide).
    If i is odd => fill just the center tile (1-wide).
    We use water = (' ', 4).
    """
    # Offsets for "3-wide": center + the 8 neighbors
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

