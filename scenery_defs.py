# FileName: scenery_defs.py
# version: 1.4
# Summary: Holds all scenery definition IDs as constants, and loads definitions from an internal Python dict.
# Tags: scenery, definitions

import os
import json

#############################
# SCENERY IDS AS CONSTANTS
#############################
TREE_TRUNK_ID       = "TreeTrunk"
TREE_TOP_ID         = "TreeTop"
ROCK_ID             = "Rock"
BRIDGE_ID           = "Bridge"
BRIDGE_END_ID       = "BridgeEnd"
RIVER_ID            = "River"
GRASS_ID            = "Grass"
PATH_ID             = "Path"
TREE_ID             = "Tree"
BRIDGE_TOOL_ID      = "BridgeTool"
SEMICOLON_FLOOR_ID  = "SemicolonFloor"
EMPTY_FLOOR_ID      = "EmptyFloor"
DEBUG_DOT_ID        = "DebugDot"

#############################
# LOAD SCENERY DEFINITIONS FROM NEW PYTHON FILE
#############################
# Instead of reading from a JSON file, we now import the dictionary directly:
from scenery_defs_data import ALL_SCENERY_DEFS

def build_forward_map():
    """
    definition_id -> (char, color_pair)
    """
    forward = {}
    for def_id, info in ALL_SCENERY_DEFS.items():
        c = info.get("ascii_char", "?")
        cp = info.get("ascii_color", 0)
        forward[def_id] = (c, cp)
    return forward

def build_reverse_map():
    """
    (char, color_pair) -> definition_id
    """
    reverse = {}
    for def_id, info in ALL_SCENERY_DEFS.items():
        c = info.get("ascii_char", "?")
        cp = info.get("ascii_color", 0)
        reverse[(c, cp)] = def_id
    return reverse

__all__ = [
    "ALL_SCENERY_DEFS",
    "build_forward_map",
    "build_reverse_map",
    "TREE_TRUNK_ID",
    "TREE_TOP_ID",
    "ROCK_ID",
    "BRIDGE_ID",
    "BRIDGE_END_ID",
    "RIVER_ID",
    "GRASS_ID",
    "PATH_ID",
    "TREE_ID",
    "BRIDGE_TOOL_ID",
    "SEMICOLON_FLOOR_ID",
    "EMPTY_FLOOR_ID",
    "DEBUG_DOT_ID",
]