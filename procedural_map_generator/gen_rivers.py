# FileName: gen_rivers.py
# version: 1.0
# Summary: Handles river spawning, from choosing edge points to thickening the water path.
# Tags: map, generation, rivers

import random

def spawn_rivers(grid, width, height, min_rivers=1, max_rivers=2):
    """
    Spawns a certain number of rivers (default 1-2). Each river starts on one
    edge, ends on the opposite edge, etc.
    """
    river_count = random.randint(min_rivers, max_rivers)
    for _ in range(river_count):
        start, end = pick_opposite_edges(width, height)
        path = trace_river_path_improved(start, end, width, height)
        fill_river_alternate_widths(grid, path, width, height)

def pick_opposite_edges(width, height):
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
    (sx, sy) = start
    (ex, ey) = end
    path = []
    curx, cury = sx, sy
    path.append((curx, cury))

    import math
    max_steps = (abs(ex - sx) + abs(ey - sy)) * 3

    for _ in range(max_steps):
        if (curx, cury) == (ex, ey):
            break
        dx = ex - curx
        dy = ey - cury

        if abs(dx) <= 1 and abs(dy) <= 1:
            curx, cury = ex, ey
            path.append((curx, cury))
            break

        do_diagonal = (random.random() < 0.3 and dx != 0 and dy != 0)
        if do_diagonal:
            sxn = 1 if dx > 0 else -1
            syn = 1 if dy > 0 else -1
            pattern_type = random.choice([0, 1])
            if pattern_type == 0:
                steps = [(sxn, 0), (sxn, 0), (0, syn)]
            else:
                steps = [(0, syn), (sxn, 0), (sxn, 0)]
        else:
            if abs(dx) > abs(dy):
                sxn = 1 if dx > 0 else -1
                steps = [(sxn, 0)] * random.randint(1, 2)
            else:
                syn = 1 if dy > 0 else -1
                steps = [(0, syn)] * random.randint(1, 2)

        for (mx, my) in steps:
            if (curx, cury) == (ex, ey):
                break
            curx += mx
            cury += my
            if curx < 0:
                curx = 0
            elif curx >= width:
                curx = width - 1
            if cury < 0:
                cury = 0
            elif cury >= height:
                cury = height - 1
            path.append((curx, cury))
            if (curx, cury) == (ex, ey):
                break

    if (curx, cury) != (ex, ey):
        path.append((ex, ey))

    return path

def fill_river_alternate_widths(grid, path, width, height):
    """
    For each index i in the path:
      if i is even => fill the tile + radius around it with water
      if i is odd  => fill just the center tile
    We store water as (' ', 'white_on_blue').
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
                    grid[ny][nx] = (' ', 'white_on_blue')
        else:
            # 1-wide
            grid[y][x] = (' ', 'white_on_blue')