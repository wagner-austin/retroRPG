# FileName: controls_play.py
# version: 2.18
#
# Summary: Play-mode only actions (e.g. chopping or mining).
#          No direct curses or curses-based code. We rely on IGameRenderer for UI tasks.
#
# Tags: controls, input, play

from scenery_data.scenery_core import get_objects_at, remove_scenery
from utils_main import get_front_tile

def handle_play_actions(action, model, renderer, full_redraw_needed, mark_dirty_func):
    """
    Play-mode only actions: e.g. INTERACT => chop/mine, gather resources, etc.
    """
    # If the editor is active, ignore play actions
    if model.context.enable_editor_commands:
        return full_redraw_needed

    player = model.player
    from_scenery = model.placed_scenery

    if action == "INTERACT":
        fx, fy = get_front_tile(player)
        tile_objs = get_objects_at(from_scenery, fx, fy)
        found_something = False
        removed_objs = []

        # Chop a TreeTrunk
        trunk = next((o for o in tile_objs if o.definition_id == "TreeTrunk"), None)
        if trunk:
            found_something = True
            removed_objs.append(trunk)
            player.wood += 1
            full_redraw_needed = True

            # If a TreeTop is directly above the trunk, remove it as well
            top_objs = get_objects_at(from_scenery, fx, fy - 1)
            top_o = next((o for o in top_objs if o.definition_id == "TreeTop"), None)
            if top_o:
                removed_objs.append(top_o)

            # Schedule respawn if enabled
            if model.context.enable_respawn:
                sublist = [(obj.x, obj.y, obj.definition_id) for obj in removed_objs]
                model.respawn_list.append({"countdown": 50, "objects": sublist})

        # Mine a Rock
        rock_o = next((o for o in tile_objs if o.definition_id == "Rock"), None)
        if rock_o:
            found_something = True
            removed_objs.append(rock_o)
            player.stone += 1
            full_redraw_needed = True

            # Schedule respawn if enabled
            if model.context.enable_respawn:
                sublist = [(rock_o.x, rock_o.y, rock_o.definition_id)]
                model.respawn_list.append({"countdown": 50, "objects": sublist})

        # Remove the objects we found
        if found_something:
            for ro in removed_objs:
                remove_scenery(from_scenery, ro)
                mark_dirty_func(ro.x, ro.y)

            # Provide visual feedback for action
            model.action_flash_info = (fx, fy, 1)
            mark_dirty_func(fx, fy)

    return full_redraw_needed
