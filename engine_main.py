# FileName: engine_main.py
# version: 2.11
# Summary: Core game loop integrating updates (NPCs, respawns, network) and rendering each frame.
# Tags: engine, main, loop

import curses

from engine_camera import (
    update_camera_with_deadzone,
    center_camera_on_player,
    partial_scroll_vertical,
    partial_scroll_horizontal
)
from engine_render import (
    draw_layers,
    mark_dirty,
    update_partial_tiles_in_view
)
from ui_main import draw_screen_frame
from color_init import color_pairs
from scenery_main import (
    get_placeable_scenery_defs,
    apply_tile_effects,
    get_scenery_def_id_at
)
from model_main import GameModel
from controls_main import (
    handle_common_keys,
    handle_editor_keys,
    handle_play_keys
)
from engine_respawn import handle_respawns
from engine_actionflash import update_action_flash
from engine_npc import update_npcs
from engine_network import handle_network
from engine_transition import handle_transitions
from engine_framerate import manage_framerate


class GameContext:
    def __init__(self, mode_name="play"):
        self.mode_name = mode_name
        self.enable_editor_commands = False
        self.enable_sliding = False
        self.enable_respawn = False
        self.require_bridge_supplies = False
        self.enable_monster_ai = False
        self.enable_damage = False

        if mode_name == "editor":
            self.enable_editor_commands = True
            self.enable_sliding = False
            self.enable_respawn = False
            self.enable_monster_ai = False
            self.enable_damage = False
        elif mode_name == "play":
            self.enable_editor_commands = False
            self.enable_sliding = True
            self.enable_respawn = True


def run_engine(stdscr,
               context,
               player,
               placed_scenery,
               respawn_list=None,
               map_top_offset=3,
               world_width=100,
               world_height=60,
               loaded_map_filename=None):
    """
    Main loop for both play and editor modes.

    :param loaded_map_filename: If not None, quick-save overwrites this file;
                               else we prompt for a new filename.
    """
    model = GameModel()
    model.player = player
    model.world_width = world_width
    model.world_height = world_height
    model.context = context

    # Store the loaded filename in the model
    model.loaded_map_filename = loaded_map_filename

    # Convert 'placed_scenery' into a dict-of-lists if needed
    if isinstance(placed_scenery, dict):
        model.placed_scenery = placed_scenery
    else:
        dict_scenery = {}
        for obj in placed_scenery:
            if hasattr(obj, 'x') and hasattr(obj, 'y'):
                dict_scenery.setdefault((obj.x, obj.y), []).append(obj)
        model.placed_scenery = dict_scenery

    # Optionally store the respawn list
    if respawn_list:
        model.respawn_list = respawn_list

    # If in editor mode, load placeable items
    if context.enable_editor_commands:
        dynamic_defs = get_placeable_scenery_defs()
        model.editor_scenery_list = [(def_id, None, None) for def_id in dynamic_defs]

    # Non-blocking input
    stdscr.nodelay(True)
    stdscr.timeout(0)

    # Center camera
    center_camera_on_player(model, stdscr, map_top_offset)

    def full_redraw(stdscr):
        stdscr.clear()
        draw_screen_frame(stdscr, "UI_CYAN")

        # Editor or inventory line
        if model.context.enable_editor_commands and model.editor_scenery_list:
            current_def_id = model.editor_scenery_list[model.editor_scenery_index][0]
            try:
                stdscr.addstr(
                    1, 2,
                    f"Editor Mode - Selected: {current_def_id}",
                    curses.color_pair(color_pairs["WHITE_TEXT"])
                )
            except:
                pass
        else:
            inv_text = (
                f"Inventory: Gold={model.player.gold}, "
                f"Wood={model.player.wood}, "
                f"Stone={model.player.stone}"
            )
            try:
                stdscr.addstr(
                    1, 2,
                    inv_text,
                    curses.color_pair(color_pairs["WHITE_TEXT"])
                )
            except:
                pass

        model.dirty_tiles.clear()

    model.full_redraw_needed = True

    while True:
        key = stdscr.getch()
        did_move = False

        # CAMERA
        max_scr_rows, max_scr_cols = stdscr.getmaxyx()
        visible_cols = max_scr_cols
        visible_rows = max_scr_rows - map_top_offset

        old_cam_x, old_cam_y = model.camera_x, model.camera_y
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
            if dy in (1, -1):
                partial_scroll_vertical(model, stdscr, dy, map_top_offset)
            if dx in (1, -1):
                partial_scroll_horizontal(model, stdscr, dx, map_top_offset)

        if key != -1:
            did_move, should_quit = handle_common_keys(key, model, stdscr, lambda x, y: mark_dirty(model, x, y))
            if should_quit:
                break

            model.full_redraw_needed = handle_editor_keys(
                key,
                model,
                stdscr,
                model.full_redraw_needed,
                lambda x, y: mark_dirty(model, x, y)
            )
            model.full_redraw_needed = handle_play_keys(
                key,
                model,
                model.full_redraw_needed,
                lambda x, y: mark_dirty(model, x, y)
            )

        # ENGINE UPDATES
        handle_network(model)
        update_npcs(model, lambda x, y: mark_dirty(model, x, y))
        handle_respawns(model, lambda x, y: mark_dirty(model, x, y))

        # Sliding
        if model.context.enable_sliding and not did_move:
            tile_def_id = get_scenery_def_id_at(
                model.player.x,
                model.player.y,
                model.placed_scenery
            )
            old_x, old_y = model.player.x, model.player.y
            apply_tile_effects(
                model.player,
                tile_def_id,
                model.placed_scenery,
                is_editor=model.context.enable_editor_commands,
                world_width=model.world_width,
                world_height=model.world_height
            )
            if (model.player.x, model.player.y) != (old_x, old_y):
                mark_dirty(model, old_x, old_y)
                mark_dirty(model, model.player.x, model.player.y)

        update_action_flash(model, lambda x, y: mark_dirty(model, x, y))
        handle_transitions(model, lambda x, y: mark_dirty(model, x, y))

        # DRAW
        if model.full_redraw_needed:
            full_redraw(stdscr)
            for wx in range(model.camera_x, min(model.camera_x + visible_cols, model.world_width)):
                for wy in range(model.camera_y, min(model.camera_y + visible_rows, model.world_height)):
                    model.dirty_tiles.add((wx, wy))
            model.full_redraw_needed = False

        update_partial_tiles_in_view(
            stdscr,
            model.player,
            model.placed_scenery,
            model.camera_x,
            model.camera_y,
            map_top_offset,
            model.dirty_tiles,
            action_flash_info=model.action_flash_info,
            world_width=model.world_width,
            world_height=model.world_height
        )
        model.dirty_tiles.clear()

        draw_layers(stdscr, model)
        manage_framerate(20)