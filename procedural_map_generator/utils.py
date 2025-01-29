# FileName: utils.py
# version: 1.1
# Summary: Shared helper functions for random distribution, BFS, or coordinate checks used by generation scripts.
# Tags: map, generation, utils

from collections import deque
from typing import List, Tuple, Callable

def manhattan_dist(x1: int, y1: int, x2: int, y2: int) -> int:
    """
    Returns the Manhattan distance between (x1, y1) and (x2, y2).
    """
    return abs(x1 - x2) + abs(y1 - y2)


def compute_distance_map_bfs(
    width: int,
    height: int,
    start_coords: List[Tuple[int, int]],
    passable_func: Callable[[int, int], bool]
) -> List[List[int]]:
    """
    Multi-source BFS that computes a distance map from all 'start_coords'.
    Any tile for which passable_func(x, y) is True can be traversed.
    Returns a 2D list 'distance_map[y][x]' with BFS distance from the nearest start.
    Unreachable tiles remain a large default (999999).
    """
    INF = 999999
    distance_map = [[INF] * width for _ in range(height)]
    queue = deque()

    # Initialize the queue with the starting coords
    for (sx, sy) in start_coords:
        if 0 <= sx < width and 0 <= sy < height:
            distance_map[sy][sx] = 0
            queue.append((sx, sy))

    # BFS
    while queue:
        cx, cy = queue.popleft()
        current_dist = distance_map[cy][cx]
        for (nx, ny) in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
            if 0 <= nx < width and 0 <= ny < height:
                if passable_func(nx, ny):
                    if distance_map[ny][nx] > current_dist + 1:
                        distance_map[ny][nx] = current_dist + 1
                        queue.append((nx, ny))

    return distance_map


def flood_fill_bfs(
    width: int,
    height: int,
    start_x: int,
    start_y: int,
    match_func: Callable[[int, int], bool]
) -> List[Tuple[int, int]]:
    """
    A BFS that returns the connected region of coordinates for which match_func(x, y) is True.
    Starting from (start_x, start_y), it collects all valid neighbors.
    """
    if not (0 <= start_x < width and 0 <= start_y < height):
        return []

    if not match_func(start_x, start_y):
        return []

    visited = set()
    queue = deque()
    queue.append((start_x, start_y))
    visited.add((start_x, start_y))

    directions = [(0,1), (0,-1), (1,0), (-1,0)]
    region_coords = []

    while queue:
        cx, cy = queue.popleft()
        region_coords.append((cx, cy))

        for (dx, dy) in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    if match_func(nx, ny):
                        visited.add((nx, ny))
                        queue.append((nx, ny))

    return region_coords