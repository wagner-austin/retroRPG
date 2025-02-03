# FileName: where_scenery_lives.py
# version: 1.0
# Summary: Holds the dictionary that was previously in scenery_defs_data.json, now using string-based color_name instead of numeric ascii_color.
# Tags: data, scenery

ALL_SCENERY_DEFS = {
    "TreeTrunk": {
        "ascii_char": "|",
        "color_name": "yellow_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/tree_trunk.png"
    },
    "TreeTop": {
        "ascii_char": "§",
        "color_name": "green_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/tree_top.png"
    },
    "Rock": {
        "ascii_char": "o",
        "color_name": "white_on_black",
        "blocking": True,
        "placeable": True,
        "tile_image": "assets/tiles/rock.png"
    },
    "Bridge": {
        "ascii_char": "#",
        "color_name": "yellow_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/bridge.png"
    },
    "BridgeEnd": {
        "ascii_char": "l",
        "color_name": "yellow_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/bridge_end.png"
    },
    "River": {
        "ascii_char": " ",
        "color_name": "white_on_blue",
        "blocking": True,
        "placeable": True,
        "tile_image": "assets/tiles/river.png"
    },
    "Grass": {
        "ascii_char": " ",
        "color_name": "white_on_green",
        "blocking": False,
        "placeable": True,
        "tile_image": "assets/tiles/grass.png"
    },
    "Path": {
        "ascii_char": " ",
        "color_name": "black_on_yellow",
        "blocking": False,
        "placeable": True,
        "tile_image": "assets/tiles/path.png"
    },
    "Tree": {
        "ascii_char": "T",
        "color_name": "green_on_white",
        "blocking": True,
        "placeable": True,
        "tile_image": "assets/tiles/tree.png"
    },
    "BridgeTool": {
        "ascii_char": "=",
        "color_name": "yellow_on_black",
        "blocking": False,
        "placeable": True,
        "tile_image": "assets/tiles/bridge_tool.png"
    },
    "SemicolonFloor": {
        "ascii_char": ";",
        "color_name": "yellow_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/semicolon_floor.png"
    },
    "EmptyFloor": {
        "ascii_char": " ",
        "color_name": "white_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/empty_floor.png"
    },
    "DebugDot": {
        "ascii_char": ".",
        "color_name": "red_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/debug_dot.png"
    }
}