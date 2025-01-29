# FileName: ui_main.py
# version: 2.8
# Summary: Provides functions and helpers for drawing frames, labels, etc.
# Tags: ui, rendering, curses

import curses
from color_init import color_pairs
from animator_draw import draw_border, draw_art
from curses_utils import safe_addstr, get_color_attr, parse_two_color_names, safe_addch

INSTRUCTION_COLOR_NAME = "UI_MAGENTA"
BORDER_COLOR_NAME      = "UI_CYAN"
TITLE_COLOR_NAME       = "UI_WHITE_ON_BLUE"
TEXT_COLOR_NAME        = "YELLOW_TEXT"
ART_COLOR_NAME         = "ASCII_ART"

UI_FONT_CONFIG = {
    "font_color_name": TEXT_COLOR_NAME,
    "font_size": None,
    "font_type": None,
}

def set_ui_font_config(**kwargs):
    for key, val in kwargs.items():
        if key in UI_FONT_CONFIG:
            UI_FONT_CONFIG[key] = val

def draw_title(stdscr: curses.window, text: str, row: int = 1, color_name: str = TITLE_COLOR_NAME) -> None:
    """
    Draw a title in bold at (row, col=2). If out of bounds, does nothing.
    """
    max_h, max_w = stdscr.getmaxyx()
    if row < 0 or row >= max_h:
        return
    col = 2

    attr = get_color_attr(color_name, bold=True)
    safe_addstr(stdscr, row, col, text, attr, clip_borders=True)

def draw_instructions(stdscr: curses.window,
                      lines: list[str],
                      from_bottom: int = 2,
                      color_name: str = INSTRUCTION_COLOR_NAME) -> None:
    """
    Draws a list of instruction lines near the bottom of the screen.
    """
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

def draw_screen_frame(stdscr: curses.window, color_name: str = BORDER_COLOR_NAME) -> None:
    """
    Draws a border around the screen, plus a "Debug mode" label if debug is enabled.
    """
    draw_border(stdscr, color_name)
    try:
        import debug
        if debug.DEBUG_CONFIG["enabled"]:
            max_h, max_w = stdscr.getmaxyx()
            label = "Debug mode: On"
            col = max_w - len(label) - 2
            dbg_attr = get_color_attr("WHITE_TEXT")
            # We'll pass clip_borders=False only if we truly want to place at col= max_w-2
            # But we do want to be inside the border, so let's keep clip_borders=True
            safe_addstr(stdscr, 0, col, label, dbg_attr, clip_borders=False)
    except:
        pass

def draw_text(stdscr: curses.window,
              row: int,
              col: int,
              text: str,
              fg: str = "white",
              bg: str = "black",
              bold: bool = False,
              underline: bool = False) -> None:
    """
    Draw text at (row, col) with a direct FG_on_BG approach,
    e.g. draw_text(..., fg="light_gray", bg="black", bold=True).
    """
    pair_name = f"{fg}_on_{bg}"
    attr = get_color_attr(pair_name, bold=bold, underline=underline)
    safe_addstr(stdscr, row, col, text, attr, clip_borders=True)