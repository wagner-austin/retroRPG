# FileName: scenery_objects_main.py
# version: 2.1
# Summary: Manages object-specific logic (Rocks, Trees, Bridges, etc.).
#          Now imports placement functions from scenery_placement_utils
# Tags: scenery, objects

from scenery_defs import (
    ROCK_ID, TREE_ID, TREE_TRUNK_ID, TREE_TOP_ID,
    BRIDGE_ID, BRIDGE_END_ID, RIVER_ID, BRIDGE_TOOL_ID
)
from scenery_core import (
    get_objects_at,  # If you still need direct usage here
    remove_scenery,
    append_scenery
)
# Import the shared placement functions from the new file
from scenery_placement_utils import (
    place_scenery_item,
    place_tree,
    place_bridge_across_river
)

# If you have any other object-specific logic, you can place it here.
# For instance, code that checks item usage or special object collisions.
# But the actual "place_*" methods are now in scenery_placement_utils.

# (No duplication here anymore!)
