# FileName: engine_main.py
# version: 2.15 (call center_camera_on_player at startup)
# Summary: Core game loop with no direct curses references.
# Tags: engine, main, loop

from engine_camera import update_camera_with_deadzone, center_camera_on_player
from engine_framerate import manage_framerate
from controls_main import (
    handle_common_keys,
    handle_editor_keys,
    handle_play_keys
)
from engine_respawn import handle_respawns
from engine_actionflash import update_action_flash
from engine_npc import update_npcs
from engine_network import handle_network
from scenery_main import (
    get_scenery_def_id_at,
    apply_tile_effects
)
import debug


def run_engine(model, context, input_func, renderer):
    """
    The main logic loop, with no direct curses calls:
      - model: GameModel
      - context: GameContext
      - input_func: a callable returning an int key (or -1 if none)
      - renderer: an object with methods like get_visible_size(), on_camera_move(...),
                  full_redraw(...), update_dirty_tiles(...), prompt_yes_no(...).
    We keep running until model.should_quit = True.
    """
    model.context = context

    # 1) Immediately center the camera on the player before the loop starts.
    visible_cols, visible_rows = renderer.get_visible_size()
    center_camera_on_player(model, visible_cols, visible_rows)

    model.full_redraw_needed = True
    model.should_quit = False

    # Main loop
    while not model.should_quit:
        # 2) Get input
        key = input_func()  # Typically from curses

        # 3) Handle keys
        if key != -1:
            did_move, want_quit = handle_common_keys(key, model, renderer, lambda x, y: mark_dirty(model, x, y))
            if want_quit:
                model.should_quit = True

            model.full_redraw_needed = handle_editor_keys(
                key,
                model,
                renderer,
                model.full_redraw_needed,
                lambda x, y: mark_dirty(model, x, y)
            )
            model.full_redraw_needed = handle_play_keys(
                key,
                model,
                model.full_redraw_needed,
                lambda x, y: mark_dirty(model, x, y)
            )

        # 4) Camera logic
        old_cam_x, old_cam_y = model.camera_x, model.camera_y
        visible_cols, visible_rows = renderer.get_visible_size()
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
                renderer.on_camera_move(dx, dy, model)

        # 5) Game updates
        handle_network(model)
        update_npcs(model, lambda x, y: mark_dirty(model, x, y))
        handle_respawns(model, lambda x, y: mark_dirty(model, x, y))

        # sliding
        if context.enable_sliding and key == -1:
            tile_def_id = get_scenery_def_id_at(model.player.x, model.player.y, model.placed_scenery)
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

        # 6) Rendering
        if model.full_redraw_needed:
            renderer.full_redraw(model)
            model.dirty_tiles.clear()
            model.full_redraw_needed = False
        else:
            renderer.update_dirty_tiles(model)
            model.dirty_tiles.clear()

        # 7) Limit framerate
        manage_framerate(20)


def mark_dirty(model, x, y):
    """
    Marks a single tile (x,y) as 'dirty' => must be re-rendered.
    """
    model.dirty_tiles.add((x, y))