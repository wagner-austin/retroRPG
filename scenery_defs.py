# FileName: scenery_defs.py
# version: 1.3
# Summary: Holds all scenery definitions (ASCII + future tile info),
#          plus the build_forward_map and build_reverse_map functions.
#          Updated so TREE_TOP_ID is green-on-black for the top of the tree.
# Tags: scenery, definitions

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
# ALL_SCENERY_DEFS DICTIONARY
#############################
ALL_SCENERY_DEFS = {
    TREE_TRUNK_ID: {
        "ascii_char": "|",
        "ascii_color": 2,  # "yellow_on_black" from your legacy color map
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/tree_trunk.png",
    },
    TREE_TOP_ID: {
        "ascii_char": "§",
        "ascii_color": 1,  # "green_on_black" => top of the tree is green font on black background
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/tree_top.png",
    },
    ROCK_ID: {
        "ascii_char": "o",
        "ascii_color": 3,  # "white_on_black"
        "blocking": True,
        "placeable": True,
        "tile_image": "assets/tiles/rock.png",
    },
    BRIDGE_ID: {
        "ascii_char": "#",
        "ascii_color": 2,
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/bridge.png",
    },
    BRIDGE_END_ID: {
        "ascii_char": "l",
        "ascii_color": 2,
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/bridge_end.png",
    },
    RIVER_ID: {
        "ascii_char": " ",
        "ascii_color": 4,  # "white_on_blue"
        "blocking": True,
        "placeable": True,
        "tile_image": "assets/tiles/river.png",
    },
    GRASS_ID: {
        "ascii_char": " ",
        "ascii_color": 5,  # "white_on_green"
        "blocking": False,
        "placeable": True,
        "tile_image": "assets/tiles/grass.png",
    },
    PATH_ID: {
        "ascii_char": " ",
        "ascii_color": 8,  # "black_on_yellow"
        "blocking": False,
        "placeable": True,
        "tile_image": "assets/tiles/path.png",
    },
    TREE_ID: {
        "ascii_char": "T",
        "ascii_color": 7,  # "green_on_white"
        "blocking": True,
        "placeable": True,
        "tile_image": "assets/tiles/tree.png",
    },
    BRIDGE_TOOL_ID: {
        "ascii_char": "=",
        "ascii_color": 2,  # "yellow_on_black"
        "blocking": False,
        "placeable": True,
        "tile_image": "assets/tiles/bridge_tool.png",
    },
    SEMICOLON_FLOOR_ID: {
        "ascii_char": ";",
        "ascii_color": 12, # "yellow_on_black"
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/semicolon_floor.png",
    },
    EMPTY_FLOOR_ID: {
        "ascii_char": " ",
        "ascii_color": 16, # "white_on_black"
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/empty_floor.png",
    },
    DEBUG_DOT_ID: {
        "ascii_char": ".",
        "ascii_color": 17, # "red_on_black"
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/debug_dot.png",
    },
}

#############################
# BUILD FORWARD/REVERSE MAPS
#############################
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

##############################################################################
# EXPORTS
##############################################################################
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
    "DEBUG_DOT_ID"
]