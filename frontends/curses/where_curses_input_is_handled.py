# FileName: where_curses_input_lives.py
# version: 2.4
#
# Summary: A curses-based front-end implementing IGameInput for user interaction.
#          Updated to remove the 'y' => YES_QUIT logic, so only 'q'/ESC quits.
#          Now also maps 'i' / 'I' => SHOW_INVENTORY.
#
# Tags: curses, ui, rendering

import curses
from engine.engine_interfaces import IGameInput

class CursesGameInput(IGameInput):
    """
    Implements IGameInput for curses: get_actions() reads the keyboard buffer,
    returns a list of action strings like ["MOVE_UP", "QUIT", "INTERACT", etc.].
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        curses.curs_set(0)

    def get_actions(self):
        actions = []
        # read up to ~5 keystrokes at once
        for _ in range(5):
            key = self.stdscr.getch()
            if key == -1:
                break
            act = self._interpret_key(key)
            if act:
                actions.append(act)
        return actions

    def _interpret_key(self, key):
        # Quit => q, Q, ESC
        if key in (ord('q'), ord('Q'), 27):
            return "QUIT"

        # Movement
        if key in (ord('w'), ord('W'), curses.KEY_UP):
            return "MOVE_UP"
        if key in (ord('s'), ord ('S'), curses.KEY_DOWN):
            return "MOVE_DOWN"
        if key in (ord('a'), ord ('A'), curses.KEY_LEFT):
            return "MOVE_LEFT"
        if key in (ord('d'), ord('D'), curses.KEY_RIGHT):
            return "MOVE_RIGHT"

        # Editor toggle
        if key in (ord('e'), ord('E')):
            return "EDITOR_TOGGLE"

        # Quick-save
        if key in (ord('o'), ord('O')):
            return "SAVE_QUICK"

        # Debug
        if key in (ord('v'), ord('V')):
            return "DEBUG_TOGGLE"

        # Interact
        if key == ord(' '):
            return "INTERACT"

        # Editor keys
        if key in (ord('p'), ord('P')):
            return "PLACE_ITEM"
        if key in (ord('x'), ord ('X')):
            return "REMOVE_TOP"
        if key in (ord('u'), ord('U')):
            return "UNDO"
        if key in (ord('l'), ord('L')):
            return "NEXT_ITEM"
        if key in (ord('k'), ord('K')):
            return "PREV_ITEM"

        # Show Inventory (new)
        if key in (ord('i'), ord('I')):
            return "SHOW_INVENTORY"

        return None