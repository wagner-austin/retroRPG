# FileName: curses_scene_game.py
# version: 1.1 (removed duplicate curses setup, let renderer handle it)

"""
Summary: This scene sets up the curses-based input & renderer and calls
         run_game_loop from engine_main.
"""

from .where_curses_input_is_handled import CursesGameInput
from .curses_game_renderer import CursesGameRenderer
from engine_main import run_game_loop

def game_scene_ui(stdscr, model, context):
    """
    Sets up the curses-based input & rendering, then runs the main game loop
    with the given model & context. Returns when the loop ends.
    """

    # We only set up our input here. The renderer's curses init is done in CursesGameRenderer.
    game_input = CursesGameInput(stdscr)
    game_renderer = CursesGameRenderer(stdscr)

    # Enter the main logic loop (in engine_main).
    run_game_loop(model, context, game_input, game_renderer)