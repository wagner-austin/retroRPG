# FileName: scenery_main.py
# version: 2.1
# Summary: Manages all scenery objects (trees, rocks, bridges), including placement, removal, and collision checks.
# Tags: scenery, map, collision

#############################
# SCENERY DEFINITIONS REGISTRY
#############################

ALL_SCENERY_DEFS = {}

##############################################################################
# SCENERY IDS AS CONSTANTS
##############################################################################
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

def register_scenery(definition_id, char, color_pair, blocking, placeable):
    """
    Register one scenery "type" with its display char, color_pair,
    whether it's blocking, and whether it's placeable in the editor.
    """
    ALL_SCENERY_DEFS[definition_id] = {
        "char": char,
        "color_pair": color_pair,
        "blocking": blocking,
        "placeable": placeable
    }

def get_placeable_scenery_defs():
    """
    Returns a list of definition_ids for items that are flagged placeable=True.
    (Used by the editor mode to build scenery lists dynamically.)
    """
    return [
        def_id
        for def_id, info in ALL_SCENERY_DEFS.items()
        if info.get("placeable", False)
    ]

def build_forward_map():
    """
    definition_id -> (char, color_pair)
    """
    forward = {}
    for def_id, info in ALL_SCENERY_DEFS.items():
        forward[def_id] = (info["char"], info["color_pair"])
    return forward

def build_reverse_map():
    """
    (char, color_pair) -> definition_id
    """
    reverse = {}
    for def_id, info in ALL_SCENERY_DEFS.items():
        c = info["char"]
        cp = info["color_pair"]
        if (c, cp) not in reverse:
            reverse[(c, cp)] = def_id
    return reverse

##############################################################################
# SCENERYOBJECT CLASS
##############################################################################
class SceneryObject:
    """
    A flexible constructor:
      - If called as SceneryObject(x, y, definition_id),
        we look up (char, color_pair) from the definitions.
      - If called as SceneryObject(x, y, char, color_pair),
        we do a reverse lookup to find definition_id (if any).
    """
    def __init__(self, x, y, paramA, paramB=None):
        self.x = x
        self.y = y

        self.definition_id = None
        self.char = "?"
        self.color_pair = 0

        # Build caches once
        if not hasattr(self.__class__, "_forward_cache"):
            self.__class__._forward_cache = build_forward_map()
            self.__class__._reverse_cache = build_reverse_map()

        forward_map = self.__class__._forward_cache
        reverse_map = self.__class__._reverse_cache

        if paramB is None:
            # paramA is a definition_id
            def_id = paramA
            self.definition_id = def_id
            char_col = forward_map.get(def_id, ("?", 0))
            self.char = char_col[0]
            self.color_pair = char_col[1]
        else:
            # paramA=char, paramB=color_pair
            c = paramA
            col = paramB
            self.char = c
            self.color_pair = col
            self.definition_id = reverse_map.get((c, col), None)

##############################################################################
# DICT-OF-LISTS ACCESSOR FUNCTIONS
##############################################################################
def _append_scenery(placed_scenery, obj):
    key = (obj.x, obj.y)
    placed_scenery.setdefault(key, []).append(obj)

def _remove_scenery(placed_scenery, obj):
    key = (obj.x, obj.y)
    stack = placed_scenery.get(key, [])
    if obj in stack:
        stack.remove(obj)
        if not stack:
            del placed_scenery[key]

def _get_objects_at(placed_scenery, x, y):
    return placed_scenery.get((x, y), [])

##############################################################################
# COLLISION & LOOKUP LOGIC
##############################################################################
def is_blocked(x, y, placed_scenery):
    """
    Collisions rely on the 'blocking' field in ALL_SCENERY_DEFS.
    The topmost object on this tile decides if it's blocked.
    """
    stack = _get_objects_at(placed_scenery, x, y)
    if not stack:
        return False

    top_obj = stack[-1]  # topmost
    info = ALL_SCENERY_DEFS.get(top_obj.definition_id, None)
    if info and info.get("blocking", False):
        return True
    return False

def get_stacked_objs(x, y, placed_scenery):
    """
    Return the entire stack of objects at (x, y), from bottom to top.
    """
    return _get_objects_at(placed_scenery, x, y)

def get_topmost_obj(x, y, placed_scenery):
    stack = _get_objects_at(placed_scenery, x, y)
    if stack:
        return stack[-1]
    return None

def get_scenery_def_id_at(x, y, placed_scenery):
    top_obj = get_topmost_obj(x, y, placed_scenery)
    if top_obj:
        return top_obj.definition_id
    return None

def get_scenery_color_at(x, y, placed_scenery):
    top_obj = get_topmost_obj(x, y, placed_scenery)
    if top_obj:
        return top_obj.color_pair
    return 0

##############################################################################
# PLACEMENT LOGIC
##############################################################################
def place_scenery_item(def_id, player, placed_scenery, mark_dirty_func,
                       is_editor=False, world_width=100, world_height=60):
    """
    Places the given scenery (by def_id) at the player's position (or bridging).
    Returns a list of the newly placed objects (for undo).
    """
    newly_placed = []

    if def_id == BRIDGE_TOOL_ID:
        if is_editor:
            # Possibly placing a series of bridge tiles across a river
            # We'll store only the newly-added tiles in 'newly_placed'
            new_objs = place_bridge_across_river(player, placed_scenery, mark_dirty_func,
                                                 world_width=world_width,
                                                 world_height=world_height,
                                                 is_editor=True)
            newly_placed.extend(new_objs)

    elif def_id == TREE_ID:
        if is_editor:
            # Places trunk + top
            trunk_obj, top_obj = place_tree(player, placed_scenery, mark_dirty_func)
            newly_placed.append(trunk_obj)
            if top_obj:
                newly_placed.append(top_obj)
        else:
            # If not in editor, just place a single T tile
            obj = _place_single_tile(player.x, player.y, TREE_ID,
                                     placed_scenery, mark_dirty_func)
            newly_placed.append(obj)
    else:
        # Place any single-tile scenery
        obj = _place_single_tile(player.x, player.y, def_id,
                                 placed_scenery, mark_dirty_func)
        newly_placed.append(obj)

    return newly_placed

def place_tree(player, placed_scenery, mark_dirty_func):
    px, py = player.x, player.y
    trunk_obj = SceneryObject(px, py, TREE_TRUNK_ID)
    _append_scenery(placed_scenery, trunk_obj)
    mark_dirty_func(px, py)

    top_obj = None
    if py > 0:
        top_obj = SceneryObject(px, py - 1, TREE_TOP_ID)
        _append_scenery(placed_scenery, top_obj)
        mark_dirty_func(px, py - 1)

    return trunk_obj, top_obj

def place_bridge_across_river(player, placed_scenery, mark_dirty_func,
                              world_width=100, world_height=60,
                              is_editor=False):
    dx = dy = 0
    if player.last_move_direction == "up":
        dy = -1
    elif player.last_move_direction == "down":
        dy = 1
    elif player.last_move_direction == "left":
        dx = -1
    elif player.last_move_direction == "right":
        dx = 1

    cx = player.x + dx
    cy = player.y + dy

    from_scenery = placed_scenery
    water_tiles = []
    while 0 <= cx < world_width and 0 <= cy < world_height:
        tile_objs = _get_objects_at(from_scenery, cx, cy)
        found_river = None
        for obj in tile_objs:
            if obj.definition_id == RIVER_ID:
                found_river = obj
                break
        if not found_river:
            break
        water_tiles.append(found_river)
        cx += dx
        cy += dy

    if not water_tiles:
        return []  # nothing changed

    newly_placed = []

    # Remove them, place Bridge
    for wobj in water_tiles:
        _remove_scenery(from_scenery, wobj)

        # Also remove any "BridgeEnd"
        tile_objs = _get_objects_at(from_scenery, wobj.x, wobj.y)
        endpoints = [o for o in tile_objs if o.definition_id == BRIDGE_END_ID]
        for e in endpoints:
            _remove_scenery(from_scenery, e)

        new_bridge = SceneryObject(wobj.x, wobj.y, BRIDGE_ID)
        _append_scenery(from_scenery, new_bridge)
        mark_dirty_func(wobj.x, wobj.y)
        newly_placed.append(new_bridge)

    # Place BridgeEnd at each side
    start_x = water_tiles[0].x - dx
    start_y = water_tiles[0].y - dy
    end_x   = water_tiles[-1].x + dx
    end_y   = water_tiles[-1].y + dy

    for (ex, ey) in [(start_x, start_y), (end_x, end_y)]:
        if 0 <= ex < world_width and 0 <= ey < world_height:
            tile_objs = _get_objects_at(from_scenery, ex, ey)
            has_bridge = any(o.definition_id == BRIDGE_ID for o in tile_objs)
            is_river   = any(o.definition_id == RIVER_ID  for o in tile_objs)
            if not has_bridge and not is_river:
                bend = SceneryObject(ex, ey, BRIDGE_END_ID)
                _append_scenery(from_scenery, bend)
                mark_dirty_func(ex, ey)
                newly_placed.append(bend)

    return newly_placed

def _place_single_tile(x, y, def_id, placed_scenery, mark_dirty_func):
    obj = SceneryObject(x, y, def_id)
    _append_scenery(placed_scenery, obj)
    mark_dirty_func(x, y)
    return obj

##############################################################################
# TILE EFFECT LOGIC
##############################################################################
def apply_tile_effects(player, tile_def_id, placed_scenery,
                       is_editor=False, world_width=100, world_height=60):
    """
    Called each frame (or movement) to handle special tile logic, e.g. 'Path'.
    If tile_def_id == "Path", we slide the player in last_move_direction until blocked.
    """
    if tile_def_id == PATH_ID:
        old_x, old_y = player.x, player.y
        player.move(player.last_move_direction, world_width, world_height, placed_scenery)
        # stops sliding if blocked

##############################################################################
# REGISTER SCENERY DEFINITIONS
# (We now use the constants above)
##############################################################################
register_scenery(TREE_TRUNK_ID,       "|", 2,  True,  False)
register_scenery(TREE_TOP_ID,         "§", 1,  False, False)
register_scenery(ROCK_ID,             "o", 3,  True,  True)
register_scenery(BRIDGE_ID,           "#", 2,  False, False)
register_scenery(BRIDGE_END_ID,       "l", 2,  False, False)
register_scenery(RIVER_ID,            " ", 4,  True,  True)
register_scenery(GRASS_ID,            " ", 5,  False, True)
register_scenery(PATH_ID,             " ", 8,  False, True)
register_scenery(TREE_ID,             "T", 7,  True,  True)
register_scenery(BRIDGE_TOOL_ID,      "=", 2,  False, True)
register_scenery(SEMICOLON_FLOOR_ID,  ";", 16, False, False)
register_scenery(EMPTY_FLOOR_ID,      " ", 16, False, False)
register_scenery(DEBUG_DOT_ID,        ".", 17, False, False)

##############################################################################
# EXPORTS
##############################################################################
__all__ = [
    "ALL_SCENERY_DEFS",
    "SceneryObject",
    "place_scenery_item",
    "apply_tile_effects",
    "_append_scenery",
    "_remove_scenery",
    "_get_objects_at",
    "register_scenery",
    "get_placeable_scenery_defs",
    "is_blocked",
    "get_stacked_objs",
    "get_topmost_obj",
    "get_scenery_def_id_at",
    "get_scenery_color_at",

    # Added constants
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

    "build_forward_map",
    "build_reverse_map",
]