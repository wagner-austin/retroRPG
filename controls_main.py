# FileName: controls_main.py
# version: 2.14
# Summary: Interprets user input actions for both play and editor modes.
#          No direct curses usage; we rely on action strings from IGameInput.
# Tags: controls, input, main

import time
import debug
from scenery_main import (
    get_objects_at,
    remove_scenery,
    append_scenery
)
from utils_main import get_front_tile

def handle_common_actions(action, model, renderer, mark_dirty_func):
    """
    Handle actions that apply to BOTH play and editor modes:
      - YES_QUIT => user pressed 'y' after a quit prompt
      - SAVE_QUICK => quick save
      - MOVE_UP / MOVE_DOWN / MOVE_LEFT / MOVE_RIGHT => movement
      - DEBUG_TOGGLE => toggles debug
      - EDITOR_TOGGLE => toggles editor mode
    """
    player = model.player
    context = model.context

    did_move = False
    should_quit = False

    def _perform_quick_save():
        """Called when user triggers SAVE_QUICK."""
        if not renderer:
            return
        if not hasattr(renderer, "get_curses_window"):
            return
        ui_win = renderer.get_curses_window()
        if not ui_win:
            return

        from curses_frontend.curses_map_ui import save_map_ui
        if model.loaded_map_filename:
            # Overwrite existing
            save_map_ui(
                ui_win,
                model.placed_scenery,
                player=model.player,
                world_width=model.world_width,
                world_height=model.world_height,
                filename_override=model.loaded_map_filename
            )
        else:
            # Prompt user for new name
            save_map_ui(
                ui_win,
                model.placed_scenery,
                player=model.player,
                world_width=model.world_width,
                world_height=model.world_height,
                filename_override=None
            )
        model.full_redraw_needed = True

    def _prompt_yes_no(question):
        """Use renderer's 'prompt_yes_no' if available."""
        if not renderer:
            return False
        if not hasattr(renderer, "prompt_yes_no"):
            return False
        return renderer.prompt_yes_no(question)

    # ACTION HANDLERS:

    if action == "YES_QUIT":
        # "YES_QUIT" typically means user confirmed they want to quit
        if model.loaded_map_filename:
            _perform_quick_save()
            should_quit = True
        else:
            # Generated => ask user
            save_decision = _prompt_yes_no("Save this generated map? (y/n)")
            if save_decision:
                _perform_quick_save()
            should_quit = True
        return (did_move, should_quit)

    elif action == "MOVE_UP":
        for _ in range(debug.DEBUG_CONFIG["walk_speed_multiplier"]):
            old_x, old_y = player.x, player.y
            player.move("up", model.world_width, model.world_height, model.placed_scenery)
            if (player.x, player.y) != (old_x, old_y):
                mark_dirty_func(old_x, old_y)
                mark_dirty_func(player.x, player.y)
                did_move = True

    elif action == "MOVE_DOWN":
        for _ in range(debug.DEBUG_CONFIG["walk_speed_multiplier"]):
            old_x, old_y = player.x, player.y
            player.move("down", model.world_width, model.world_height, model.placed_scenery)
            if (player.x, player.y) != (old_x, old_y):
                mark_dirty_func(old_x, old_y)
                mark_dirty_func(player.x, player.y)
                did_move = True

    elif action == "MOVE_LEFT":
        for _ in range(debug.DEBUG_CONFIG["walk_speed_multiplier"]):
            old_x, old_y = player.x, player.y
            player.move("left", model.world_width, model.world_height, model.placed_scenery)
            if (player.x, player.y) != (old_x, old_y):
                mark_dirty_func(old_x, old_y)
                mark_dirty_func(player.x, player.y)
                did_move = True

    elif action == "MOVE_RIGHT":
        for _ in range(debug.DEBUG_CONFIG["walk_speed_multiplier"]):
            old_x, old_y = player.x, player.y
            player.move("right", model.world_width, model.world_height, model.placed_scenery)
            if (player.x, player.y) != (old_x, old_y):
                mark_dirty_func(old_x, old_y)
                mark_dirty_func(player.x, player.y)
                did_move = True

    elif action == "DEBUG_TOGGLE":
        debug.toggle_debug()
        model.full_redraw_needed = True

    elif action == "EDITOR_TOGGLE":
        if context.mode_name == "play":
            context.mode_name = "editor"
            context.enable_editor_commands = True
            context.enable_sliding = False
            context.enable_respawn = False

            if not model.editor_scenery_list:
                from scenery_main import get_placeable_scenery_defs
                dynamic_defs = get_placeable_scenery_defs()
                model.editor_scenery_list = [(def_id, None, None) for def_id in dynamic_defs]
        else:
            context.mode_name = "play"
            context.enable_editor_commands = False
            context.enable_sliding = True
            context.enable_respawn = True

        model.full_redraw_needed = True

    elif action == "SAVE_QUICK":
        _perform_quick_save()

    return (did_move, should_quit)


def handle_editor_actions(action, model, renderer, full_redraw_needed, mark_dirty_func):
    """
    Editor-only actions:
      - PLACE_ITEM => place object
      - REMOVE_TOP => remove topmost
      - UNDO => undo
      - NEXT_ITEM => cycle object forward
      - PREV_ITEM => cycle object backward
    """
    if not model.context.enable_editor_commands:
        return full_redraw_needed

    editor_scenery_list = model.editor_scenery_list
    editor_scenery_index = model.editor_scenery_index
    player = model.player

    from scenery_main import (
        place_scenery_item,
        get_objects_at,
        remove_scenery,
        append_scenery
    )

    if action == "PLACE_ITEM":
        if editor_scenery_list:
            current_def_id = editor_scenery_list[editor_scenery_index][0]
            newly_placed = place_scenery_item(
                current_def_id,
                player,
                model.placed_scenery,
                mark_dirty_func=mark_dirty_func,
                is_editor=True,
                world_width=model.world_width,
                world_height=model.world_height
            )
            if newly_placed:
                model.editor_undo_stack.append(("added", newly_placed))

    elif action == "REMOVE_TOP":
        px, py = player.x, player.y
        tile_objs = get_objects_at(model.placed_scenery, px, py)
        if tile_objs:
            top_obj = tile_objs[-1]
            remove_scenery(model.placed_scenery, top_obj)
            model.editor_undo_stack.append(("removed", [top_obj]))
            mark_dirty_func(px, py)

    elif action == "UNDO":
        if model.editor_undo_stack:
            action_type, objects_list = model.editor_undo_stack.pop()
            if action_type == "added":
                for obj in reversed(objects_list):
                    remove_scenery(model.placed_scenery, obj)
                    mark_dirty_func(obj.x, obj.y)
            elif action_type == "removed":
                for obj in objects_list:
                    append_scenery(model.placed_scenery, obj)
                    mark_dirty_func(obj.x, obj.y)

    elif action == "NEXT_ITEM":
        if editor_scenery_list:
            model.editor_scenery_index = (editor_scenery_index + 1) % len(editor_scenery_list)
            full_redraw_needed = True

    elif action == "PREV_ITEM":
        if editor_scenery_list:
            model.editor_scenery_index = (editor_scenery_index - 1) % len(editor_scenery_list)
            full_redraw_needed = True

    return full_redraw_needed


def handle_play_actions(action, model, renderer, full_redraw_needed, mark_dirty_func):
    """
    Play-mode only actions: e.g. INTERACT => chop/mine
    """
    if model.context.enable_editor_commands:
        return full_redraw_needed

    player = model.player
    from_scenery = model.placed_scenery
    if action == "INTERACT":
        fx, fy = get_front_tile(player)
        tile_objs = get_objects_at(from_scenery, fx, fy)
        found_something = False
        removed_objs = []

        trunk = next((o for o in tile_objs if o.definition_id == "TreeTrunk"), None)
        if trunk:
            found_something = True
            removed_objs.append(trunk)
            player.wood += 1
            full_redraw_needed = True

            top_objs = get_objects_at(from_scenery, fx, fy - 1)
            top_o = next((o for o in top_objs if o.definition_id == "TreeTop"), None)
            if top_o:
                removed_objs.append(top_o)

            if model.context.enable_respawn:
                sublist = [(obj.x, obj.y, obj.definition_id) for obj in removed_objs]
                model.respawn_list.append({"countdown": 50, "objects": sublist})

        rock_o = next((o for o in tile_objs if o.definition_id == "Rock"), None)
        if rock_o:
            found_something = True
            removed_objs.append(rock_o)
            player.stone += 1
            full_redraw_needed = True

            if model.context.enable_respawn:
                sublist = [(rock_o.x, rock_o.y, rock_o.definition_id)]
                model.respawn_list.append({"countdown": 50, "objects": sublist})

        if found_something:
            for ro in removed_objs:
                remove_scenery(from_scenery, ro)
                mark_dirty_func(ro.x, ro.y)

            model.action_flash_info = (fx, fy, 1)
            mark_dirty_func(fx, fy)

    return full_redraw_needed