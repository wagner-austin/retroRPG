# FileName: play_main.py
# version: 2.2
# Summary: Top-level function for entering Play mode, linking user’s map choice to the engine loop.
# Tags: play, main, engine

import curses
from map_io_ui import load_map_ui  # CHANGED: we now import from map_io_ui
from play_runner import parse_and_run_play


def play_main(stdscr):
    """
    Called when user chooses "Play" from main menu.
    We always load a map in play mode, then inside the game,
    you can press 'e' to toggle to the editor if desired.
    """
    while True:
        selection = load_map_ui(stdscr)  # formerly load_map(stdscr) from map_io_main
        if not selection:
            # user canceled => back to main menu
            return

        # If load_map_ui returns a tuple (e.g. ("EDIT", filename)),
        # we pass the second item into parse_and_run_play.
        if isinstance(selection, tuple):
            action_type, actual_map = selection[0], selection[1]
            if action_type == "EDIT_GENERATE":
                parse_and_run_play(stdscr, actual_map, is_generated=True)
            else:
                # e.g. ("EDIT", "filename")
                parse_and_run_play(stdscr, actual_map, is_generated=False)
        elif isinstance(selection, dict):
            # user chose "Generate a new map" => run in play mode
            parse_and_run_play(stdscr, selection, is_generated=True)
        else:
            # user picked an existing file => play mode
            parse_and_run_play(stdscr, selection, is_generated=False)