RetroRPG

A simple 2D retro RPG prototype in Python using the curses library. You can play and edit maps directly in-game.

Summary

Play Mode: Move the player around, gather resources, fight enemies (if any).

Editor Mode: Place and delete tiles, undo your changes, and save the map anytime.

Maps: Generate a new map or load an existing one.

Quick-Save: Overwrite if the map has a file name; else prompt for a new name.


Installation

Make sure you have Python 3.7+.

Ensure that curses is available on your system.

Linux/macOS: Usually installed by default.

Windows: Use WSL or a library like UniCurses.

Android (via Pydroid 3): Should work as is.


Clone or download the retroRPG_current folder.

(Optional) Create a virtual environment and install dependencies if you have a requirements.txt.


How to Run

1. Open a terminal or console in the retroRPG_current/ directory.


2. Run python main_RetroRPG.py (or python3 main_RetroRPG.py) to launch the game.


3. You’ll see a main menu to load a map or generate a new one.



Usage & Play Instructions

After selecting a map (or generating one), you start in Play Mode.

Press e to toggle Editor Mode.

Press y in either mode to quit back to the menu.

Press o at any time to quick-save.

If the map was loaded from an existing file, it overwrites that file.

If the map has no file name (newly generated), it prompts for a save name.



Controls (Play Mode)

W, A, S, D (uppercase or lowercase) or arrow keys: Move the player.

Space: Chop or mine the tile in front of the player.

e: Switch to Editor Mode.

o: Quick-save.

v: Toggle debug mode (if enabled).

y: Quit back to the menu.


Controls (Editor Mode)

p: Place the currently selected tile at the player’s location.

x: Delete the topmost tile at the player’s location.

u: Undo last place or delete action.

l: Move to the next scenery item in the list.

k: Move to the previous scenery item in the list.

e: Switch back to Play Mode.

o: Quick-save (same overwrite/prompt logic).

y: Quit back to the menu.


Player Coordinates

The game saves player_x and player_y in the map file, so when you reload the same map, you spawn where you left off.


Contact / License

The code is free to use or modify.

Have fun with RetroRPG! Feel free to extend or adapt it.


