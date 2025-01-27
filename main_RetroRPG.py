# FileName: main_RetroRPG.py
# version: 1.4 (UPDATED for home/load screen art animation)
# Primary entry point for the Retro RPG app.)

import curses
from animator_main import animate_home_screen

from play_main import play_main
from color_init import init_colors

def run_game(stdscr):
    # Runs the main menu, then dispatches to either Play or Quit.
    # Let the terminal size stabilize before we draw anything
    curses.napms(100)

    init_colors()
    while True:
        choice = animate_home_screen(stdscr)  # Now uses animate_home_screen from animator_main
        if choice == 1:
            # "Play" is chosen
            play_main(stdscr)
        elif choice == 2:
            # "Quit" is chosen
            break

def main():
    curses.wrapper(run_game)

if __name__ == "__main__":
    main()