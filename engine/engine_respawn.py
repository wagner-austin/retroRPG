# FileName: engine_respawn.py
# version: 1.2
# Summary: Tracks and respawns resources (trees, rocks) after a set countdown.
# Tags: engine, respawn, resources, scenery

from scenery.scenery_core import SceneryObject, append_scenery

def handle_respawns(model, mark_dirty_func):
    """
    If context.enable_respawn is true, decrement countdowns and respawn.
    We expect each entry in model.respawn_list to look like:
      { "countdown": N, "objects": [ (x, y, definition_id), ... ] }

    Once countdown <= 0, we re-create those objects.
    """
    if not model.context.enable_respawn:
        return

    # Make a copy of the list so we can remove entries safely
    for r in model.respawn_list[:]:
        r["countdown"] -= 1
        if r["countdown"] <= 0:
            # Time to respawn these objects
            for (sx, sy, def_id) in r["objects"]:
                new_obj = SceneryObject(sx, sy, def_id)
                append_scenery(model.placed_scenery, new_obj)
                mark_dirty_func(sx, sy)

            # remove from the list
            model.respawn_list.remove(r)