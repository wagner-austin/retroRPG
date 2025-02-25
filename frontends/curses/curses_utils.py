# FileName: curses_utils.py
#
# version: 1.1
#
# Summary: Provides safe curses output helpers and color attribute assembly.
#
# Tags: curses, utils

import curses
from typing import Optional
from .curses_color_init import color_pairs

def get_color_attr(color_name: str, bold: bool = False, blink: bool = False, underline: bool = False) -> int:
    """
    Given a color name like "white_on_black", returns a curses attribute
    including optional BOLD/BLINK/UNDERLINE bits.
    """
    pair_id = color_pairs.get(color_name, 0)
    attr = curses.color_pair(pair_id)
    if bold:
        attr |= curses.A_BOLD
    if blink:
        attr |= curses.A_BLINK
    if underline:
        attr |= curses.A_UNDERLINE
    return attr

def parse_two_color_names(fg_bg: str) -> (str, str):
    """
    Splits a string like "white_on_blue" into ("white","blue").
    If invalid, returns ("white","black").
    """
    parts = fg_bg.split("_on_")
    if len(parts) == 2:
        return parts[0], parts[1]
    return ("white", "black")

def _clip_coords_for_borders(row: int, col: int, max_h: int, max_w: int) -> (int, int):
    if row < 1 or row > (max_h - 2):
        return (-1, -1)
    if col < 1:
        col = 1
    if col > (max_w - 2):
        return (-1, -1)
    return (row, col)

def _truncate_for_borders_text(col: int, text: str, max_w: int) -> str:
    available_width = (max_w - 2) - col + 1
    if available_width < 1:
        return ""
    return text[:available_width]

def safe_addstr(stdscr: curses.window, row: int, col: int, text: str, attr: int, clip_borders: bool = True) -> None:
    """
    Safely add a string at (row, col), optionally clipping to a border if clip_borders=True.
    """
    max_h, max_w = stdscr.getmaxyx()

    if clip_borders:
        row2, col2 = _clip_coords_for_borders(row, col, max_h, max_w)
        if row2 < 0 or col2 < 0:
            return
        text = _truncate_for_borders_text(col2, text, max_w)
        if not text:
            return
        row, col = row2, col2
    else:
        if row < 0 or row >= max_h:
            return
        if col < 0 or col >= max_w:
            return
        available_width = max_w - col
        if available_width < 1:
            return
        text = text[:available_width]

    try:
        stdscr.addstr(row, col, text, attr)
    except curses.error:
        pass

def safe_addch(stdscr: curses.window, row: int, col: int, ch, attr: int, clip_borders: bool = True) -> None:
    """
    Safely add a single character at (row, col).
    """
    max_h, max_w = stdscr.getmaxyx()

    if clip_borders:
        row2, col2 = _clip_coords_for_borders(row, col, max_h, max_w)
        if row2 < 0 or col2 < 0:
            return
        row, col = row2, col2
    else:
        if row < 0 or row >= max_h:
            return
        if col < 0 or col >= max_w:
            return

    try:
        stdscr.addch(row, col, ch, attr)
    except curses.error:
        pass