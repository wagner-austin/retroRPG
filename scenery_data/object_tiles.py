# FileName: object_tiles.py

# version 1.0

# Summary: modify object tiles here

# Tags: objects, scenery


# scenery_data/object_tiles.py

OBJECT_TILES = {
    "TreeTrunk": {
        "ascii_char": "|",
        "color_name": "yellow_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/tree_trunk.png",
        "layer": "objects"
    },
    "TreeTop": {
        "ascii_char": "§",
        "color_name": "green_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/tree_top.png",
        "layer": "objects"
    },
    "Rock": {
        "ascii_char": "o",
        "color_name": "white_on_black",
        "blocking": True,
        "placeable": True,
        "tile_image": "assets/tiles/rock.png",
        "layer": "objects"
    },
    "Bridge": {
        "ascii_char": "#",
        "color_name": "yellow_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/bridge.png",
        "layer": "objects"
    },
     "BridgeTool": {
        "ascii_char": "=",
        "color_name": "yellow_on_black",
        "blocking": False,
        "placeable": True,
        "tile_image": "assets/tiles/bridge_tool.png",
        "layer": "items"
    },
    "BridgeEnd": {
        "ascii_char": "l",
        "color_name": "yellow_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/bridge_end.png",
        "layer": "objects"
    },
    "Tree": {
        "ascii_char": "T",
        "color_name": "green_on_white",
        "blocking": True,
        "placeable": True,
        "tile_image": "assets/tiles/tree.png",
        "layer": "objects"
    }
}
