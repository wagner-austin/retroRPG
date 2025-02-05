# FileName: engine_main.py
# version: 3.3 (modified for infinite map)
#
# Summary: Core game loop. Camera logic has no bounding now.
# Tags: engine, main, loop

from engine_camera import update_camera_with_deadzone, center_camera_on_player
from engine_framerate import manage_framerate
from controls.controls_main import (
    handle_common_actions,
    handle_editor_actions,
    handle_play_actions,
)
from engine_respawn import handle_respawns
from engine_actionflash import update_action_flash
from engine_npc import update_npcs
from engine_network import handle_network
from scenery_data.scenery_placement import  apply_tile_effects
from scenery_data.scenery_core import get_scenery_def_id_at

def run_game_loop(model, context, game_input, game_renderer):
    """
    The main loop. We remove any bounding references to world_width/height 
    and rely on the updated camera logic (which doesn't clamp).
    """

    model.context = context

    # Center camera on player once at start
    visible_cols, visible_rows = game_renderer.get_visible_size()
    center_camera_on_player(model, visible_cols, visible_rows)

    model.full_redraw_needed = True
    model.should_quit = False

    # We'll track camera movement each frame
    model.ui_scroll_dx = 0
    model.ui_scroll_dy = 0

    while not model.should_quit:
        # 1) Gather input
        actions = game_input.get_actions()
        for act in actions:
            did_move, want_quit = handle_common_actions(
                act, model, game_renderer, lambda x, y: mark_dirty(model, x, y)
            )
            if want_quit:
                model.should_quit = True
                break

            model.full_redraw_needed = handle_editor_actions(
                act, model, game_renderer, model.full_redraw_needed,
                lambda x, y: mark_dirty(model, x, y)
            )
            model.full_redraw_needed = handle_play_actions(
                act, model, game_renderer, model.full_redraw_needed,
                lambda x, y: mark_dirty(model, x, y)
            )

        if model.should_quit:
            break

        # 2) Update camera logic (no bounding)
        old_cam_x, old_cam_y = model.camera_x, model.camera_y
        visible_cols, visible_rows = game_renderer.get_visible_size()

        # world_width & world_height no longer clamp the camera
        model.camera_x, model.camera_y = update_camera_with_deadzone(
            model.player.x,
            model.player.y,
            model.camera_x,
            model.camera_y,
            visible_cols,
            visible_rows,
            dead_zone=2
        )
        dx = model.camera_x - old_cam_x
        dy = model.camera_y - old_cam_y

        model.ui_scroll_dx = dx
        model.ui_scroll_dy = dy

        # If camera jumped more than 1 tile, force full redraw
        if abs(dx) > 1 or abs(dy) > 1:
            model.full_redraw_needed = True

        # 3) Game updates
        handle_network(model)
        update_npcs(model, lambda x, y: mark_dirty(model, x, y))
        handle_respawns(model, lambda x, y: mark_dirty(model, x, y))

        # Optional sliding
        if context.enable_sliding and not actions:
            tile_def_id = get_scenery_def_id_at(
                model.player.x, model.player.y, model.placed_scenery
            )
            old_px, old_py = model.player.x, model.player.y
            apply_tile_effects(
                model.player,
                tile_def_id,
                model.placed_scenery,
                is_editor=context.enable_editor_commands
                # ignoring world_width / world_height
            )
            if (model.player.x, model.player.y) != (old_px, old_py):
                mark_dirty(model, old_px, old_py)
                mark_dirty(model, model.player.x, model.player.y)

        update_action_flash(model, lambda x, y: mark_dirty(model, x, y))

        # 4) Rendering
        game_renderer.render(model)
        model.dirty_tiles.clear()

        # 5) Framerate
        manage_framerate(20)

def mark_dirty(model, x, y):
    model.dirty_tiles.add((x, y))