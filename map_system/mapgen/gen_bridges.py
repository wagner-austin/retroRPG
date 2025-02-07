# gen_bridges.py
# Connects disconnected grass regions via bridging.

import random

def connect_grass_regions_with_bridges(grid, grass_regions):
    """
    For each pair of distinct grass regions, place bridging (#) across water so that
    everything eventually becomes one big connected set.
    Bridges have:
      - end-posts (char='l', color=2) at the first/last bridging cell
      - bridging (char='#', color=2) in between
    """
    if not grass_regions:
        return

    master = grass_regions[0]
    for i in range(1, len(grass_regions)):
        region = grass_regions[i]
        a = random.choice(master)
        b = random.choice(region)
        build_bridge_with_posts(grid, a, b)
        # add region to master
        master.extend(region)

def build_bridge_with_posts(grid, start, end):
    """
    Draw a straight line from start->end. For each water cell in the line, place bridging:
      - 'l' for the first/last bridging cell (end-post)
      - '#' for bridging in between
    """
    (sx, sy) = start
    (ex, ey) = end
    dx = ex - sx
    dy = ey - sy
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return

    for i in range(steps + 1):
        t = i / steps
        cx = int(round(sx + t * dx))
        cy = int(round(sy + t * dy))

        if grid[cy][cx] is not None:
            ch, cpair = grid[cy][cx]
            # If currently water, we place bridging
            if ch == ' ' and cpair == 4:
                # End-post vs. middle bridging
                if i == 0 or i == steps:
                    grid[cy][cx] = ('l', 2)
                else:
                    grid[cy][cx] = ('#', 2)
