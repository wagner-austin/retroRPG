# FileName: scenery_placement.py
# version 1.0

# Summary: Manages tile placement, layering, collision checks, tile effects, and a SceneryObject class.

# Tags: scenery, placement

from scenery_data.scenery_manager import ALL_SCENERY_DEFS, layer_for_def_id

# Example constants if you still want easy references:
RIVER_ID         = "River"
GRASS_ID         = "Grass"
PATH_ID          = "Path"
EMPTY_FLOOR_ID   = "EmptyFloor"
DEBUG_DOT_ID     = "DebugDot"
BRIDGE_TOOL_ID   = "BridgeTool"
SEMICOLON_FLOOR_ID = "SemicolonFloor"
# etc.

##############################################################################
# SCENERY OBJECT CLASS
##############################################################################
class SceneryObject:
    def __init__(self, x, y, definition_id):
        """
        A simpler constructor using ALL_SCENERY_DEFS lookups.
        """
        self.x = x
        self.y = y
        self.definition_id = definition_id

        # Get default char/color from the dictionary:
        info = ALL_SCENERY_DEFS.get(definition_id, {})
        self.char = info.get("ascii_char", "?")
        self.color_pair = info.get("color_name", "white_on_black")

##############################################################################
# REGISTER / GET PLACEABLE
##############################################################################
def register_scenery(definition_id, char, color_pair, blocking, placeable, layer="objects"):
    """
    Dynamically add or override a tile definition in ALL_SCENERY_DEFS at runtime.
    """
    ALL_SCENERY_DEFS[definition_id] = {
        "ascii_char": char,
        "color_name": color_pair,
        "blocking": blocking,
        "placeable": placeable,
        "layer": layer
    }

def get_placeable_scenery_defs():
    """
    Return a list of def_ids from ALL_SCENERY_DEFS that have 'placeable': True
    """
    return [
        def_id
        for def_id, info in ALL_SCENERY_DEFS.items()
        if info.get("placeable", False)
    ]

##############################################################################
# LAYERED STORAGE HELPERS
##############################################################################
def _init_tile_layers(placed_scenery, x, y, layer_name):
    """
    Ensure (x,y) has an entry in placed_scenery, and that 'layer_name' key exists.
    If it's a floor layer, store a single object or None;
    if it's objects/items/entities, store a list.
    """
    if (x, y) not in placed_scenery:
        placed_scenery[(x, y)] = {}

    tile_dict = placed_scenery[(x, y)]
    if layer_name not in tile_dict:
        if layer_name == "floor":
            tile_dict[layer_name] = None
        else:
            tile_dict[layer_name] = []

def append_scenery(placed_scenery, obj):
    """
    Insert 'obj' into placed_scenery at the correct layer.
    If it's a floor tile, store exactly one floor object and push any old floor
    into '_prev_floor' if different.
    """
    x, y = obj.x, obj.y
    layer_name = layer_for_def_id(obj.definition_id)
    _init_tile_layers(placed_scenery, x, y, layer_name)

    tile_dict = placed_scenery[(x, y)]
    if layer_name == "floor":
        old_floor = tile_dict["floor"]
        if old_floor and old_floor.definition_id != obj.definition_id:
            tile_dict["_prev_floor"] = old_floor
        tile_dict["floor"] = obj
    else:
        tile_dict[layer_name].append(obj)

def remove_scenery(placed_scenery, obj):
    """
    Remove 'obj' from placed_scenery. If it's the floor, restore _prev_floor if possible.
    If tile ends up empty, fill it with 'EmptyFloor'.
    """
    x, y = obj.x, obj.y
    if (x, y) not in placed_scenery:
        return

    tile_dict = placed_scenery[(x, y)]
    layer_name = layer_for_def_id(obj.definition_id)

    if layer_name == "floor":
        if tile_dict.get("floor") == obj:
            if tile_dict.get("_prev_floor"):
                tile_dict["floor"] = tile_dict["_prev_floor"]
                tile_dict["_prev_floor"] = None
            else:
                tile_dict["floor"] = None
    else:
        if obj in tile_dict.get(layer_name, []):
            tile_dict[layer_name].remove(obj)

    # If everything is empty now, place "EmptyFloor"
    if (tile_dict.get("floor") is None
        and not tile_dict.get("objects", [])
        and not tile_dict.get("items", [])
        and not tile_dict.get("entities", [])):
        tile_dict["floor"] = SceneryObject(x, y, EMPTY_FLOOR_ID)
        tile_dict["_prev_floor"] = None

def get_objects_at(placed_scenery, x, y):
    """
    Return a flat list of all SceneryObjects at (x,y).
    """
    if (x, y) not in placed_scenery:
        return []

    tile_dict = placed_scenery[(x, y)]
    merged = []
    if "floor" in tile_dict and tile_dict["floor"]:
        merged.append(tile_dict["floor"])
    merged.extend(tile_dict.get("objects", []))
    merged.extend(tile_dict.get("items", []))
    merged.extend(tile_dict.get("entities", []))
    return merged

def get_topmost_obj(placed_scenery, x, y):
    """
    Return whichever SceneryObject is 'on top' (the last in the stacked layers).
    """
    stack = get_objects_at(placed_scenery, x, y)
    return stack[-1] if stack else None

def get_scenery_def_id_at(x, y, placed_scenery):
    """
    Return the definition_id of the topmost object at (x,y).
    """
    top = get_topmost_obj(placed_scenery, x, y)
    return top.definition_id if top else None

def get_scenery_color_at(x, y, placed_scenery):
    """
    Return the color_pair of the topmost object at (x,y).
    """
    top = get_topmost_obj(placed_scenery, x, y)
    return top.color_pair if top else "white_on_black"

def is_blocked(x, y, placed_scenery):
    """
    If the tile is empty, it's not blocked. Otherwise, check the topmost object's 'blocking'.
    """
    top = get_topmost_obj(placed_scenery, x, y)
    if not top:
        return False
    tile_info = ALL_SCENERY_DEFS.get(top.definition_id, {})
    return bool(tile_info.get("blocking", False))

##############################################################################
# TILE EFFECT LOGIC
##############################################################################
def apply_tile_effects(player, tile_def_id, placed_scenery,
                       is_editor=False, world_width=100, world_height=60):
    """
    Example: automatically 'slide' the player if they step on a Path tile.
    """
    if tile_def_id == PATH_ID:
        player.move(player.last_move_direction, world_width, world_height, placed_scenery)
        # If blocked, the move won't succeed, effectively ending the 'slide'.