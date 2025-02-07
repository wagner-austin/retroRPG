# FileName: utils_main.py
# version: 3.5
# Summary: Contains miscellaneous utility functions and BFS helpers.
# Tags: utils, general

import shutil
from typing import Tuple
#from collections import deque


def get_terminal_size():
    try:
        size = shutil.get_terminal_size(fallback=(0, 0))
        if size.lines >= 10 and size.columns >= 10:
            return size.lines, size.columns
    except:
        print ("unable to determine terminal size")
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