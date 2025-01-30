# FileName: highlight_selector.py
# version: 1.4
# Summary: Provides a single, globally configurable highlight/selector system.
# Tags: selector, highlight, effects

import curses
from color_init import color_pairs
from curses_utils import safe_addstr, get_color_attr

GLOBAL_HIGHLIGHT_CONFIG = {
    "selected_color_name":   "YELLOW_TEXT",   # was "UI_YELLOW", unified
    "unselected_color_name": "WHITE_TEXT",
    "effect_name":           "REVERSE_BLINK",
    "speed_factor":          5,
}

def get_global_selector_config():
    return GLOBAL_HIGHLIGHT_CONFIG

def get_selector_effect_attrs(effect="REVERSE_BLINK",
                              frame=0,
                              speed_factor=10) -> int:
    toggle_state = (frame // speed_factor) % 2
    if effect == "NONE":
        return curses.A_NORMAL
    elif effect == "REVERSE":
        return curses.A_REVERSE
    elif effect == "BLINK":
        return curses.A_BLINK
    elif effect == "REVERSE_BLINK":
        return (curses.A_REVERSE | curses.A_BLINK)
    elif effect == "FLASH":
        return curses.A_REVERSE if toggle_state == 0 else curses.A_NORMAL
    elif effect == "GLOW":
        return curses.A_BOLD if toggle_state == 0 else curses.A_NORMAL
    elif effect == "SHIMMER":
        return (curses.A_BOLD | curses.A_BLINK) if toggle_state == 0 else curses.A_NORMAL
    return curses.A_REVERSE  # fallback

def draw_global_selector_line(stdscr, row: int, text: str,
                              is_selected: bool=False,
                              frame: int=0) -> None:
    config = get_global_selector_config()
    selected_color_name   = config["selected_color_name"]
    unselected_color_name = config["unselected_color_name"]
    effect_name           = config["effect_name"]
    speed_factor          = config["speed_factor"]

    if is_selected:
        attrs = get_selector_effect_attrs(effect=effect_name, frame=frame, speed_factor=speed_factor)
        color_attr = get_color_attr(selected_color_name) | attrs
    else:
        color_attr = get_color_attr(unselected_color_name)

    safe_addstr(stdscr, row, 2, text, color_attr)