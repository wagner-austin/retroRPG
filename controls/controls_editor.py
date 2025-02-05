# FileName: controls_editor.py
# version: 2.18
#
# Summary: Editor-only actions for interpreting user input.
#          No direct curses or curses-based code. We rely on IGameRenderer for UI tasks.
#
# Tags: controls, input, editor

from scenery_data.scenery_core import get_objects_at, remove_scenery, append_scenery
from scenery_data.scenery_placement_utils import place_scenery_item

def handle_editor_actions(action, model, renderer, full_redraw_needed, mark_dirty_func):
    """
    Editor-only actions:
      - PLACE_ITEM => place object
      - REMOVE_TOP => remove topmost object
      - UNDO => undo the last change
      - NEXT_ITEM => cycle next object
      - PREV_ITEM => cycle previous object
    """
    if not model.context.enable_editor_commands:
        return full_redraw_needed

    editor_scenery_list = model.editor_scenery_list
    editor_scenery_index = model.editor_scenery_index
    player = model.player

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
                # Undo "added": remove each one
                for obj in reversed(objects_list):
                    remove_scenery(model.placed_scenery, obj)
                    mark_dirty_func(obj.x, obj.y)
            elif action_type == "removed":
                # Undo "removed": restore them
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
