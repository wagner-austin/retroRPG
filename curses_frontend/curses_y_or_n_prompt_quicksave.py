# FileName: curses_y_or_no_quicksave.py
#
# version: 1.0
#
# Summary: Provides UI-related helpers for controls, including quick-saving (which uses curses_scene_save) and yes/no prompts using the renderer.

# Tags: controls, ui

def prompt_yes_no(renderer, question):
    """
    Wrapper to ask the renderer to show a yes/no prompt. Return True if "yes".
    We keep it outside controls_main so that controls_main isn't importing UI directly.
    """
    if not renderer:
        return False
    if not hasattr(renderer, "prompt_yes_no"):
        return False
    return renderer.prompt_yes_no(question)


def perform_quick_save(model, renderer):
    """
    Performs a quick save of the map data, using curses_scene_save if we have a valid renderer.
    """
    if not renderer:
        return
    if not hasattr(renderer, "get_curses_window"):
        return

    ui_win = renderer.get_curses_window()
    if not ui_win:
        return

    from curses_frontend.curses_scene_save import save_map_ui
    player = model.player

    if model.loaded_map_filename:
        # Overwrite existing
        save_map_ui(
            ui_win,
            model.placed_scenery,
            player=player,
            world_width=model.world_width,
            world_height=model.world_height,
            filename_override=model.loaded_map_filename
        )
    else:
        # Prompt user for new name
        save_map_ui(
            ui_win,
            model.placed_scenery,
            player=player,
            world_width=model.world_width,
            world_height=model.world_height,
            filename_override=None
        )

    model.full_redraw_needed = True
