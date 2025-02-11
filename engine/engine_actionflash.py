# FileName: engine_actionflash.py
# version: 1.0
# Summary: Displays and updates short-lived visual indicators (flashes) when player chops, mines, or interacts.
# Tags: engine, feedback, effects

def update_action_flash(model, mark_dirty_func):
    """
    Decrements the action_flash_info counter. If it's done, clears it and marks dirty.
    """
    if model.action_flash_info is None:
        return

    fx, fy, count = model.action_flash_info
    count -= 1
    if count <= 0:
        model.action_flash_info = None
        mark_dirty_func(fx, fy)
    else:
        model.action_flash_info = (fx, fy, count)
        mark_dirty_func(fx, fy)