# FileName: curses_scene_game.py
# version: 1.0
#
# Summary: This scene sets up the curses-based input & renderer and calls run_game_loop from engine_main.
# 
# Tags: scene, game, curses

import curses
from .curses_input import CursesGameInput
from .curses_renderer import CursesGameRenderer
from engine_main import run_game_loop

def run_game_scene(stdscr, model, context):
    """
    Sets up the curses-based input & rendering, then runs the main game loop
    with the given model & context. Returns when the loop ends.
    """
    # Basic curses setup
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.curs_set(0)

    # Create front-end objects
    game_input = CursesGameInput(stdscr)
    game_renderer = CursesGameRenderer(stdscr)

    # Enter the main logic loop (in engine_main)
    run_game_loop(model, context, game_input, game_renderer)
