# FileName: utils.py
# version: 1.0
# Summary: Shared helper functions for random distribution, sampling, or coordinate checks used by generation scripts.
# Tags: map, generation, utils

def manhattan_dist(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)
