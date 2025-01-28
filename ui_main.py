# FileName: ui_main.py
# version: 2.6
# Summary: Provides functions and helpers for drawing frames, labels, etc.
#          Now includes a universal draw_text helper for flexible FG/BG usage.
# Tags: ui, rendering, curses

import curses
from color_init import color_pairs
from animator_draw import draw_border, draw_art

# Existing color constants or aliases (now mapped in color_init.py):
INSTRUCTION_COLOR_NAME = "UI_MAGENTA"
BORDER_COLOR_NAME      = "UI_CYAN"
TITLE_COLOR_NAME       = "UI_WHITE_ON_BLUE"
TEXT_COLOR_NAME        = "YELLOW_TEXT"
ART_COLOR_NAME         = "ASCII_ART"

# This config remains from your existing code
UI_FONT_CONFIG = {
    "font_color_name": TEXT_COLOR_NAME,
    "font_size": None,
    "font_type": None,
}

def set_ui_font_config(**kwargs):
    for key, val in kwargs.items():
        if key in UI_FONT_CONFIG:
            UI_FONT_CONFIG[key] = val

def draw_title(stdscr, text, row=1, color_name=TITLE_COLOR_NAME):
    max_h, max_w = stdscr.getmaxyx()
    if row < 0 or row >= max_h:
        return
    col = 2
    title_color = curses.color_pair(color_pairs[color_name]) | curses.A_BOLD
    truncated = text[:max_w - col - 1]
    try:
        stdscr.addstr(row, col, truncated, title_color)
    except curses.error:
        pass

def draw_instructions(stdscr, lines, from_bottom=2, color_name=INSTRUCTION_COLOR_NAME):
    h, w = stdscr.getmaxyx()
    color = curses.color_pair(color_pairs[color_name])
    start_row = h - from_bottom - len(lines)
    if start_row < 1:
        start_row = 1

    row = start_row
    for line in lines:
        if row >= h - 1:
            break
        truncated = line[:w - 4]
        try:
            stdscr.addstr(row, 2, truncated, color)
        except curses.error:
            pass
        row += 1

def draw_screen_frame(stdscr, color_name=BORDER_COLOR_NAME):
    draw_border(stdscr, color_name)
    # Show "Debug mode" in top-right if debug enabled
    try:
        import debug
        if debug.DEBUG_CONFIG["enabled"]:
            max_h, max_w = stdscr.getmaxyx()
            label = "Debug mode: On"
            col = max_w - len(label) - 2
            debug_color = curses.color_pair(color_pairs["WHITE_TEXT"])
            stdscr.addstr(0, col, label, debug_color)
    except:
        pass

# --------------------------------------------------------------------
# NEW HELPER: draw_text for direct FG/BG usage
# --------------------------------------------------------------------
def draw_text(stdscr, row, col, text,
              fg="white",
              bg="black",
              bold=False,
              underline=False):
    """
    Draw text at (row, col) with a direct FG_on_BG approach,
    e.g. draw_text(..., fg="light_gray", bg="black", bold=True).
    """
    pair_name = f"{fg}_on_{bg}"
    pair_id = color_pairs.get(pair_name, 0)  # 0 => default color if not found
    attr = curses.color_pair(pair_id)
    if bold:
        attr |= curses.A_BOLD
    if underline:
        attr |= curses.A_UNDERLINE

    max_h, max_w = stdscr.getmaxyx()
    truncated = text[: (max_w - col)]

    try:
        stdscr.addstr(row, col, truncated, attr)
    except curses.error:
        pass