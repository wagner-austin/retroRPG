# FileName: engine_respawn.py
# version: 1.1
# Summary: Tracks and respawns resources (trees, rocks) or other entities after a set timer.
# Tags: engine, respawn, resources

from scenery_main import SceneryObject, append_scenery

def handle_respawns(model, mark_dirty_func):
    """
    If context.enable_respawn is true, decrement countdowns and respawn scenery.
    Each entry in model.respawn_list is a dict like:
      { "countdown": N, "objects": [(sx, sy, schar, scolor), ...] }
    Once countdown <= 0, we respawn those objects.
    """
    if not model.context.enable_respawn:
        return

    for r in model.respawn_list[:]:
        r["countdown"] -= 1
        if r["countdown"] <= 0:
            # Time to respawn these objects
            for (sx, sy, schar, scolor) in r["objects"]:
                new_obj = SceneryObject(sx, sy, schar, scolor)
                append_scenery(model.placed_scenery, new_obj)
                mark_dirty_func(sx, sy)

            model.respawn_list.remove(r)