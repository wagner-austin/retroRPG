# FileName: engine_respawn.py
# version: 1.1 (Now uses _append_scenery for dict-based placed_scenery)

from scenery_main import SceneryObject
# We import the dictionary-friendly helper:
from scenery_main import _append_scenery

def handle_respawns(model, mark_dirty_func):
    """
    If context.enable_respawn is true, decrement countdowns and respawn scenery.
    Each entry in model.respawn_list is a dict like:
      { "countdown": N, "objects": [(sx, sy, schar, scolor), ...] }
    Once countdown <= 0, we respawn those objects at (sx, sy).
    """
    if not model.context.enable_respawn:
        return

    # We copy the list so we can safely remove entries while iterating
    for r in model.respawn_list[:]:
        r["countdown"] -= 1
        if r["countdown"] <= 0:
            # Time to respawn these objects
            for (sx, sy, schar, scolor) in r["objects"]:
                new_obj = SceneryObject(sx, sy, schar, scolor)
                # Instead of model.placed_scenery.append(...), we do:
                _append_scenery(model.placed_scenery, new_obj)
                mark_dirty_func(sx, sy)

            # Remove this entry from respawn_list now that we've respawned
            model.respawn_list.remove(r)