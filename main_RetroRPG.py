# FileName: main_RetroRPG.py
# version: 1.5
# Summary: Main entry point for RetroRPG, handling high-level init, config loading, and main menu dispatch.
# Tags: main, entry, initialization

import curses
from scene_main import scene_home_screen  # CHANGED: now using the new high-level scene
from play_main import play_main
from color_init import init_colors


def run_game(stdscr):
    # Let the terminal size stabilize before we draw anything
    curses.napms(100)

    init_colors()
    while True:
        choice = scene_home_screen(stdscr)  # was animate_home_screen
        if choice == 1:
            play_main(stdscr)
        elif choice == 2:
            break


def main():
    curses.wrapper(run_game)


if __name__ == "__main__":
    main()