# FileName: curses_common.py
#
# version: 2.9
#
# Summary: Provides functions and helpers for drawing frames, labels, etc. in curses.
#
# Tags: ui, rendering, curses

import curses
import debug
from .curses_color_init import color_pairs
from .curses_utils import safe_addstr, safe_addch, get_color_attr

def draw_title(stdscr: curses.window, text: str, row: int = 1, color_name: str = None) -> None:
    """
    Draw a title string at the given row. If color_name is not provided,
    use CURRENT_THEME's 'title_color'.
    """
    from .curses_themes import CURRENT_THEME
    if color_name is None:
        color_name = CURRENT_THEME["title_color"]

    max_h, max_w = stdscr.getmaxyx()
    if row < 0 or row >= max_h:
        return
    col = 2
    attr = get_color_attr(color_name, bold=True)
    safe_addstr(stdscr, row, col, text, attr, clip_borders=True)

def draw_instructions(stdscr: curses.window, lines: list[str], from_bottom: int = 2, color_name: str = None) -> None:
    """
    Draws a list of instruction lines near the bottom of the screen. 
    If color_name not provided, use CURRENT_THEME's 'instructions_color'.
    """
    from .curses_themes import CURRENT_THEME
    if color_name is None:
        color_name = CURRENT_THEME["instructions_color"]

    h, w = stdscr.getmaxyx()
    attr = get_color_attr(color_name)

    start_row = h - from_bottom - len(lines)
    if start_row < 1:
        start_row = 1

    row = start_row
    for line in lines:
        if row >= h - 1:
            break
        safe_addstr(stdscr, row, 2, line, attr, clip_borders=True)
        row += 1

def draw_screen_frame(stdscr: curses.window, color_name: str = None) -> None:
    """
    Draws a rectangular border around the entire screen, plus a "Debug mode" label if debug is enabled.
    If color_name not provided, use CURRENT_THEME's 'border_color'.
    """
    from .curses_themes import CURRENT_THEME
    if color_name is None:
        color_name = CURRENT_THEME["border_color"]

    h, w = stdscr.getmaxyx()
    border_attr = get_color_attr(color_name)

    # Top line
    for x in range(w):
        safe_addch(stdscr, 0, x, curses.ACS_HLINE, border_attr, clip_borders=False)
    safe_addch(stdscr, 0, 0, curses.ACS_ULCORNER, border_attr, clip_borders=False)
    safe_addch(stdscr, 0, w - 1, curses.ACS_URCORNER, border_attr, clip_borders=False)

    # Bottom line
    for x in range(w):
        safe_addch(stdscr, h - 1, x, curses.ACS_HLINE, border_attr, clip_borders=False)
    safe_addch(stdscr, h - 1, 0, curses.ACS_LLCORNER, border_attr, clip_borders=False)
    safe_addch(stdscr, h - 1, w - 1, curses.ACS_LRCORNER, border_attr, clip_borders=False)

    # Left/right
    for y in range(1, h - 1):
        safe_addch(stdscr, y, 0, curses.ACS_VLINE, border_attr, clip_borders=False)
        safe_addch(stdscr, y, w - 1, curses.ACS_VLINE, border_attr, clip_borders=False)

    # Debug label
    if debug.DEBUG_CONFIG["enabled"]:
        label = "Debug mode: On"
        col = w - len(label) - 6
        dbg_attr = get_color_attr("white_on_black")
        safe_addstr(stdscr, 0, col, label, dbg_attr, clip_borders=False)

def draw_text(stdscr: curses.window, row: int, col: int, text: str,
              fg: str = "white", bg: str = "black",
              bold: bool = False, underline: bool = False) -> None:
    """
    Draw text at (row, col) with direct FG_on_BG approach.
    """
    from .curses_utils import parse_two_color_names
    pair_name = f"{fg}_on_{bg}"
    attr = get_color_attr(pair_name, bold=bold, underline=underline)
    safe_addstr(stdscr, row, col, text, attr, clip_borders=True)