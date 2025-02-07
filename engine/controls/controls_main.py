# FileName: controls_main.py
# version: 2.18
#
# Summary: Main entry point for interpreting user actions, delegating to:
#          controls_common, controls_editor, and controls_play.
#
# Tags: controls, input, main

from .controls_common import handle_common_actions
from .controls_editor import handle_editor_actions
from .controls_play import handle_play_actions

def dispatch_action(action, model, renderer, full_redraw_needed, mark_dirty_func):
    """
    Dispatches an action to the appropriate handlers in a set sequence:
      1) Common actions
      2) Editor-only actions
      3) Play-only actions

    Returns:
      (did_move, should_quit, updated_full_redraw)
    """
    # 1) Handle common actions first
    did_move, should_quit = handle_common_actions(action, model, renderer, mark_dirty_func)

    # 2) Handle editor actions
    updated_full_redraw = handle_editor_actions(
        action, model, renderer, full_redraw_needed, mark_dirty_func
    )

    # 3) Handle play actions
    updated_full_redraw = handle_play_actions(
        action, model, renderer, updated_full_redraw, mark_dirty_func
    )

    return (did_move, should_quit, updated_full_redraw)