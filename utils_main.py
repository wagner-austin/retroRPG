# FileName: utils_main.py
# version: 3.5
# Summary: Contains miscellaneous utility functions and BFS helpers.
# Tags: utils, general

import curses
import shutil
from typing import List, Tuple, Callable
from collections import deque


def get_terminal_size():
    try:
        size = shutil.get_terminal_size(fallback=(0, 0))
        if size.lines >= 10 and size.columns >= 10:
            return size.lines, size.columns
    except:
        pass
    return 60, 40


def get_front_tile(player) -> Tuple[int, int]:
    """
    Returns the (x, y) coordinates of the tile directly in front of the player,
    based on player.last_move_direction.
    """
    fx, fy = player.x, player.y
    if player.last_move_direction == "up":
        fy -= 1
    elif player.last_move_direction == "down":
        fy += 1
    elif player.last_move_direction == "left":
        fx -= 1
    elif player.last_move_direction == "right":
        fx += 1
    return fx, fy


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
    Tiles unreachable remain at a large default (999999).
    """
    INF = 999999
    distance_map = [[INF] * width for _ in range(height)]
    queue = deque()

    # Initialize queue with starting coords
    for (sx, sy) in start_coords:
        if 0 <= sx < width and 0 <= sy < height:
            distance_map[sy][sx] = 0
            queue.append((sx, sy))

    # BFS
    while queue:
        cx, cy = queue.popleft()
        current_dist = distance_map[cy][cx]
        for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
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