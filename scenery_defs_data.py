# FileName: scenery_defs_data.py
# version: 1.0
# Summary: Holds the dictionary that was previously in scenery_defs_data.json
# Tags: data, scenery

ALL_SCENERY_DEFS = {
    "TreeTrunk": {
        "ascii_char": "|",
        "ascii_color": 2,
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/tree_trunk.png"
    },
    "TreeTop": {
        "ascii_char": "§",
        "ascii_color": 1,
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/tree_top.png"
    },
    "Rock": {
        "ascii_char": "o",
        "ascii_color": 3,
        "blocking": True,
        "placeable": True,
        "tile_image": "assets/tiles/rock.png"
    },
    "Bridge": {
        "ascii_char": "#",
        "ascii_color": 2,
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/bridge.png"
    },
    "BridgeEnd": {
        "ascii_char": "l",
        "ascii_color": 2,
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/bridge_end.png"
    },
    "River": {
        "ascii_char": " ",
        "ascii_color": 4,
        "blocking": True,
        "placeable": True,
        "tile_image": "assets/tiles/river.png"
    },
    "Grass": {
        "ascii_char": " ",
        "ascii_color": 5,
        "blocking": False,
        "placeable": True,
        "tile_image": "assets/tiles/grass.png"
    },
    "Path": {
        "ascii_char": " ",
        "ascii_color": 8,
        "blocking": False,
        "placeable": True,
        "tile_image": "assets/tiles/path.png"
    },
    "Tree": {
        "ascii_char": "T",
        "ascii_color": 7,
        "blocking": True,
        "placeable": True,
        "tile_image": "assets/tiles/tree.png"
    },
    "BridgeTool": {
        "ascii_char": "=",
        "ascii_color": 2,
        "blocking": False,
        "placeable": True,
        "tile_image": "assets/tiles/bridge_tool.png"
    },
    "SemicolonFloor": {
        "ascii_char": ";",
        "ascii_color": 12,
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/semicolon_floor.png"
    },
    "EmptyFloor": {
        "ascii_char": " ",
        "ascii_color": 16,
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/empty_floor.png"
    },
    "DebugDot": {
        "ascii_char": ".",
        "ascii_color": 17,
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/debug_dot.png"
    }
}
