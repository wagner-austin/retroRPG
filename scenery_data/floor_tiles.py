# FileName: floor_tiles.py

# version 1.0

# Summary: manage floor tiles here

# Tags: floor, scenery

# scenery_data/floor_tiles.py

FLOOR_TILES = {
    "River": {
        "ascii_char": " ",
        "color_name": "white_on_blue",
        "blocking": True,
        "placeable": True,
        "tile_image": "assets/tiles/river.png",
        "layer": "floor"
    },
    "Grass": {
        "ascii_char": " ",
        "color_name": "white_on_green",
        "blocking": False,
        "placeable": True,
        "tile_image": "assets/tiles/grass.png",
        "layer": "floor"
    },
    "Path": {
        "ascii_char": " ",
        "color_name": "black_on_yellow",
        "blocking": False,
        "placeable": True,
        "tile_image": "assets/tiles/path.png",
        "layer": "floor"
    },
    "SemicolonFloor": {
        "ascii_char": ";",
        "color_name": "yellow_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/semicolon_floor.png",
        "layer": "floor"
    },
    "EmptyFloor": {
        "ascii_char": " ",
        "color_name": "white_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/empty_floor.png",
        "layer": "floor"
    },
    "DebugDot": {
        "ascii_char": ".",
        "color_name": "red_on_black",
        "blocking": False,
        "placeable": False,
        "tile_image": "assets/tiles/debug_dot.png",
        "layer": "floor"
    }
}
