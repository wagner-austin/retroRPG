# FileName: main_RetroRPG.py
# version: 1.6 (modified to use MenuFlowManager)
# Summary: Main entry point for RetroRPG, handling high-level init, config loading, and main menu dispatch.
# Tags: main, entry, initialization

import curses
from curses_frontend.curses_color_init import init_colors
from menu_flow_manager import MenuFlowManager

def run_game(stdscr):
    # Let the terminal size stabilize before we draw anything
    curses.napms(100)

    init_colors()
    # Instead of manually looping the home scene, we delegate to our new menu flow manager
    flow_manager = MenuFlowManager(stdscr)
    flow_manager.run()

def main():
    curses.wrapper(run_game)

if __name__ == "__main__":
    main()