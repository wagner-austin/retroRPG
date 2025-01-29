# FileName: controls_main.py
# version: 2.9
# Summary: Interprets user input for both play and editor modes, including movement, undo, toggles, etc.
# Tags: controls, input, main

import curses
from scenery_main import (
    place_scenery_item,
    get_objects_at,      # renamed from _get_objects_at
    remove_scenery,      # renamed from _remove_scenery
    append_scenery       # renamed from _append_scenery
)
from utils_main import get_front_tile
import debug

def handle_common_keys(key, model, stdscr, mark_dirty_func):
    """
    Handle keys that apply to *both* play and editor modes:
      - Quitting (y)
      - Movement (WASD or arrow keys)
      - Debug toggle (v)
      - Mode switch (e)
      - Quick-save (o)
    """
    player = model.player
    context = model.context

    did_move = False
    should_quit = False

    def _perform_quick_save():
        from map_io_ui import save_map_ui
        # If we have a loaded filename, overwrite it
        if hasattr(model, "loaded_map_filename") and model.loaded_map_filename:
            save_map_ui(
                stdscr,
                model.placed_scenery,
                player=model.player,
                world_width=model.world_width,
                world_height=model.world_height,
                filename_override=model.loaded_map_filename
            )
        else:
            # Prompt for new filename
            save_map_ui(
                stdscr,
                model.placed_scenery,
                player=model.player,
                world_width=model.world_width,
                world_height=model.world_height,
                filename_override=None
            )
        model.full_redraw_needed = True

    def _prompt_yes_no(stdscr, question="Save this generated map? (y/n)"):
        max_h, max_w = stdscr.getmaxyx()
        qy = max_h - 1  # bottom row
        qx = 2
        try:
            stdscr.move(qy, 0)
            stdscr.clrtoeol()
        except:
            pass
        try:
            stdscr.addstr(qy, qx, question, curses.color_pair(0))
            stdscr.refresh()
        except:
            pass

        while True:
            c = stdscr.getch()
            if c in (ord('y'), ord('Y')):
                return True
            elif c in (ord('n'), ord('N')):
                return False

    # Quit key
    if key == ord('y'):
        # Check if it's an existing map or generated
        if model.loaded_map_filename:
            # 1) Existing map => silent quick-save, then quit
            _perform_quick_save()
            should_quit = True
        else:
            # 2) Generated map => prompt user
            save_decision = _prompt_yes_no(stdscr, "Save this generated map? (y/n)")
            if save_decision:
                _perform_quick_save()
            should_quit = True
        return (did_move, should_quit)

    # Movement
    elif key in (ord('w'), ord('W'), curses.KEY_UP):
        for _ in range(debug.DEBUG_CONFIG["walk_speed_multiplier"]):
            old_x, old_y = player.x, player.y
            player.move("up", model.world_width, model.world_height, model.placed_scenery)
            if (player.x, player.y) != (old_x, old_y):
                mark_dirty_func(old_x, old_y)
                mark_dirty_func(player.x, player.y)
                did_move = True

    elif key in (ord('s'), ord('S'), curses.KEY_DOWN):
        for _ in range(debug.DEBUG_CONFIG["walk_speed_multiplier"]):
            old_x, old_y = player.x, player.y
            player.move("down", model.world_width, model.world_height, model.placed_scenery)
            if (player.x, player.y) != (old_x, old_y):
                mark_dirty_func(old_x, old_y)
                mark_dirty_func(player.x, player.y)
                did_move = True

    elif key in (ord('a'), ord('A'), curses.KEY_LEFT):
        for _ in range(debug.DEBUG_CONFIG["walk_speed_multiplier"]):
            old_x, old_y = player.x, player.y
            player.move("left", model.world_width, model.world_height, model.placed_scenery)
            if (player.x, player.y) != (old_x, old_y):
                mark_dirty_func(old_x, old_y)
                mark_dirty_func(player.x, player.y)
                did_move = True

    elif key in (ord('d'), ord('D'), curses.KEY_RIGHT):
        for _ in range(debug.DEBUG_CONFIG["walk_speed_multiplier"]):
            old_x, old_y = player.x, player.y
            player.move("right", model.world_width, model.world_height, model.placed_scenery)
            if (player.x, player.y) != (old_x, old_y):
                mark_dirty_func(old_x, old_y)
                mark_dirty_func(player.x, player.y)
                did_move = True

    # Toggle Debug Mode
    elif key == ord('v'):
        debug.toggle_debug()
        model.full_redraw_needed = True

    # Switch between play and editor mode using 'e'
    elif key == ord('e'):
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

    # Quick-save with 'o'
    elif key == ord('o'):
        _perform_quick_save()

    return (did_move, should_quit)


def handle_editor_keys(key, model, stdscr, full_redraw_needed, mark_dirty_func):
    """
    Editor-only keys:
      - p (Place object)
      - x (Delete the topmost object at player's tile)
      - u (Undo last place or delete)
      - l, k (Next/Prev item)
    """
    if not model.context.enable_editor_commands:
        return full_redraw_needed

    editor_scenery_list = model.editor_scenery_list
    editor_scenery_index = model.editor_scenery_index
    player = model.player

    if key == ord('p'):
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

    elif key == ord('x'):
        px, py = player.x, player.y
        tile_objs = get_objects_at(model.placed_scenery, px, py)
        if tile_objs:
            top_obj = tile_objs[-1]
            remove_scenery(model.placed_scenery, top_obj)
            model.editor_undo_stack.append(("removed", [top_obj]))
            mark_dirty_func(px, py)

    elif key == ord('u'):
        if model.editor_undo_stack:
            action, objects_list = model.editor_undo_stack.pop()
            if action == "added":
                for obj in reversed(objects_list):
                    remove_scenery(model.placed_scenery, obj)
                    mark_dirty_func(obj.x, obj.y)
            elif action == "removed":
                for obj in objects_list:
                    append_scenery(model.placed_scenery, obj)
                    mark_dirty_func(obj.x, obj.y)

    elif key == ord('l'):
        if editor_scenery_list:
            model.editor_scenery_index = (editor_scenery_index + 1) % len(editor_scenery_list)
            full_redraw_needed = True

    elif key == ord('k'):
        if editor_scenery_list:
            model.editor_scenery_index = (editor_scenery_index - 1) % len(editor_scenery_list)
            full_redraw_needed = True

    return full_redraw_needed


def handle_play_keys(key, model, full_redraw_needed, mark_dirty_func):
    """
    Play-mode-specific keys, e.g. space for chop or mine.
    """
    if model.context.enable_editor_commands:
        return full_redraw_needed

    player = model.player
    from_scenery = model.placed_scenery
    if key == ord(' '):
        fx, fy = get_front_tile(player)
        found_something = False
        removed_objs = []

        tile_objs = get_objects_at(from_scenery, fx, fy)
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
                sublist = [(obj.x, obj.y, obj.char, obj.color_pair) for obj in removed_objs]
                model.respawn_list.append({"countdown": 50, "objects": sublist})

        rock_o = next((o for o in tile_objs if o.definition_id == "Rock"), None)
        if rock_o:
            found_something = True
            removed_objs.append(rock_o)
            player.stone += 1
            full_redraw_needed = True
            if model.context.enable_respawn:
                sublist = [(rock_o.x, rock_o.y, rock_o.char, rock_o.color_pair)]
                model.respawn_list.append({"countdown": 50, "objects": sublist})

        if found_something:
            for ro in removed_objs:
                remove_scenery(from_scenery, ro)
                mark_dirty_func(ro.x, ro.y)

            model.action_flash_info = (fx, fy, 1)
            mark_dirty_func(fx, fy)

    return full_redraw_needed