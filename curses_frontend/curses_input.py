# FileName: curses_input.py
#
# version: 2.2
#
# Summary: A curses-based front-end implementing IGameInput for user interaction.
#
# Tags: curses, ui, rendering

import curses
from interfaces import IGameInput

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
        # yes-quit
        if key in (ord('y'), ord('Y')):
            return "YES_QUIT"
        # quit => q, Q, ESC
        if key in (ord('q'), ord('Q'), 27):
            return "QUIT"

        # movement
        if key in (ord('w'), curses.KEY_UP):
            return "MOVE_UP"
        if key in (ord('s'), curses.KEY_DOWN):
            return "MOVE_DOWN"
        if key in (ord('a'), curses.KEY_LEFT):
            return "MOVE_LEFT"
        if key in (ord('d'), curses.KEY_RIGHT):
            return "MOVE_RIGHT"

        # editor toggle
        if key == ord('e'):
            return "EDITOR_TOGGLE"

        # quick-save
        if key == ord('o'):
            return "SAVE_QUICK"

        # debug
        if key == ord('v'):
            return "DEBUG_TOGGLE"

        # interact
        if key == ord(' '):
            return "INTERACT"

        # editor keys
        if key == ord('p'):
            return "PLACE_ITEM"
        if key == ord('x'):
            return "REMOVE_TOP"
        if key == ord('u'):
            return "UNDO"
        if key == ord('l'):
            return "NEXT_ITEM"
        if key == ord('k'):
            return "PREV_ITEM"

        return None