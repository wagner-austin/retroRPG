# FileName: engine_main.py
#
# version: 3.2
#
# Summary: Core game loop using IGameRenderer & IGameInput. Skips final render if should_quit is set.
#
# Tags: engine, main, loop

import time
import debug

from engine_camera import update_camera_with_deadzone, center_camera_on_player
from engine_framerate import manage_framerate
from controls_main import (handle_common_keys, handle_editor_keys, handle_play_keys)
from engine_respawn import handle_respawns
from engine_actionflash import update_action_flash
from engine_npc import update_npcs
from engine_network import handle_network
from scenery_main import (get_scenery_def_id_at, apply_tile_effects)


def run_game_loop(model, context, game_input, game_renderer):
    """The main logic loop, using IGameRenderer & IGameInput interfaces."""
    model.context = context

    # Center camera on player once at start
    visible_cols, visible_rows = game_renderer.get_visible_size()
    center_camera_on_player(model, visible_cols, visible_rows)

    model.full_redraw_needed = True
    model.should_quit = False

    while not model.should_quit:
        # 1) Get all actions
        actions = game_input.get_actions()
        for act in actions:
            key = map_action_to_keycode(act)
            if key is None:
                # e.g. "QUIT" or unhandled
                if act == "QUIT":
                    model.should_quit = True
                continue

            # Pass the key to old controls logic
            did_move, want_quit = handle_common_keys(
                key,
                model,
                game_renderer,
                lambda x, y: mark_dirty(model, x, y)
            )
            if want_quit:
                model.should_quit = True
                break

            model.full_redraw_needed = handle_editor_keys(
                key,
                model,
                game_renderer,
                model.full_redraw_needed,
                lambda x, y: mark_dirty(model, x, y)
            )
            model.full_redraw_needed = handle_play_keys(
                key,
                model,
                game_renderer,
                model.full_redraw_needed,
                lambda x, y: mark_dirty(model, x, y)
            )

        # If user triggered quit, skip final re-render
        if model.should_quit:
            break

        # 2) Camera logic
        old_cam_x, old_cam_y = model.camera_x, model.camera_y
        visible_cols, visible_rows = game_renderer.get_visible_size()
        model.camera_x, model.camera_y = update_camera_with_deadzone(
            model.player.x,
            model.player.y,
            model.camera_x,
            model.camera_y,
            visible_cols,
            visible_rows,
            model.world_width,
            model.world_height,
            dead_zone=2
        )
        dx = model.camera_x - old_cam_x
        dy = model.camera_y - old_cam_y

        if abs(dx) > 1 or abs(dy) > 1:
            model.full_redraw_needed = True
        else:
            if dx != 0 or dy != 0:
                game_renderer.on_camera_move(dx, dy, model)

        # 3) Game updates
        handle_network(model)
        update_npcs(model, lambda x, y: mark_dirty(model, x, y))
        handle_respawns(model, lambda x, y: mark_dirty(model, x, y))

        # sliding if no new actions
        if context.enable_sliding and not actions:
            tile_def_id = get_scenery_def_id_at(
                model.player.x,
                model.player.y,
                model.placed_scenery
            )
            old_px, old_py = model.player.x, model.player.y
            apply_tile_effects(
                model.player,
                tile_def_id,
                model.placed_scenery,
                is_editor=context.enable_editor_commands,
                world_width=model.world_width,
                world_height=model.world_height
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


def map_action_to_keycode(action):
    """Map the action string to old integer key codes (used by handle_*_keys)."""
    if action == "QUIT":
        return None
    elif action == "YES_QUIT":
        return ord('y')
    elif action == "MOVE_UP":
        return ord('w')
    elif action == "MOVE_DOWN":
        return ord('s')
    elif action == "MOVE_LEFT":
        return ord('a')
    elif action == "MOVE_RIGHT":
        return ord('d')
    elif action == "EDITOR_TOGGLE":
        return ord('e')
    elif action == "SAVE_QUICK":
        return ord('o')
    elif action == "DEBUG_TOGGLE":
        return ord('v')
    elif action == "INTERACT":
        return ord(' ')
    elif action == "REMOVE_TOP":
        return ord('x')
    elif action == "PLACE_ITEM":
        return ord('p')
    elif action == "UNDO":
        return ord('u')
    elif action == "NEXT_ITEM":
        return ord('l')
    elif action == "PREV_ITEM":
        return ord('k')
    return None