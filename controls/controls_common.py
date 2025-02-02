# FileName: controls_common.py
# version: 2.19 (modified to handle SHOW_INVENTORY action)
#
# Summary: Interprets user input actions that apply to BOTH play and editor modes.
#          No direct curses or curses-based code. We rely on IGameRenderer
#          to handle UI tasks. Inventory is displayed in a dedicated scene.
#
# Tags: controls, input, common

import debug

def handle_common_actions(action, model, renderer, mark_dirty_func):
    """
    Handle actions that apply to BOTH play and editor modes:
      - QUIT => user pressed 'q' to leave the map
      - SAVE_QUICK => quick save
      - MOVE_UP / MOVE_DOWN / MOVE_LEFT / MOVE_RIGHT => movement
      - DEBUG_TOGGLE => toggles debug
      - EDITOR_TOGGLE => toggles editor mode
      - SHOW_INVENTORY => display an inventory screen
    """
    player = model.player
    context = model.context

    did_move = False
    should_quit = False

    if action == "QUIT":
        # The user pressed 'q' (or ESC) to leave the map.
        if model.loaded_map_filename:
            # If there's a filename, do a quick-save and quit
            renderer.quick_save(model)
            should_quit = True
        else:
            # For a generated map with no filename, ask user if they want to save
            if renderer.prompt_yes_no(""""Save this generated map? (y/n)"""):
                renderer.quick_save(model)
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
        # Toggle between play and editor contexts
        if context.mode_name == "play":
            context.mode_name = "editor"
            context.enable_editor_commands = True
            context.enable_sliding = False
            context.enable_respawn = False

            if not model.editor_scenery_list:
                from scenery_defs import get_placeable_scenery_defs
                dynamic_defs = get_placeable_scenery_defs()
                model.editor_scenery_list = [(def_id, None, None) for def_id in dynamic_defs]
        else:
            context.mode_name = "play"
            context.enable_editor_commands = False
            context.enable_sliding = True
            context.enable_respawn = True

        model.full_redraw_needed = True

    elif action == "SAVE_QUICK":
        # The user triggered a quick save
        renderer.quick_save(model)

    elif action == "SHOW_INVENTORY":
        # Display the dedicated inventory screen
        curses_window = renderer.get_curses_window()
        if curses_window:
            from curses_frontend.curses_scene_inventory import show_inventory_screen
            show_inventory_screen(curses_window, model)

            # Force a full redraw after closing the inventory
            model.full_redraw_needed = True

    return (did_move, should_quit)