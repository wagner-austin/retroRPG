# FileName: scenery_tile_effects.py
# version 1.0

# Summary: Manages tile effects.

# Tags: scenery, placement

PATH_ID          = "Path"

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