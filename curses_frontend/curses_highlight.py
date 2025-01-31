# FileName: curses_highlight.py
#
# version: 1.4
#
# Summary: Provides a single, globally configurable highlight/selector system.
#
# Tags: selector, highlight, effects

import curses
from .curses_color_init import color_pairs
from .curses_utils import safe_addstr, get_color_attr
from .curses_themes import CURRENT_THEME

GLOBAL_HIGHLIGHT_CONFIG = {
    # We set them to None; we will fetch from CURRENT_THEME at runtime.
    "selected_color_name":   None,
    "unselected_color_name": None,
    "effect_name":           "REVERSE_BLINK",
    "speed_factor":          5,
}

def get_global_selector_config():
    """
    Returns the global highlight config, filling in selected/unselected
    color names from the CURRENT_THEME if they are None.
    """
    config = GLOBAL_HIGHLIGHT_CONFIG.copy()
    if config["selected_color_name"] is None:
        config["selected_color_name"] = CURRENT_THEME["highlight_selected_color"]
    if config["unselected_color_name"] is None:
        config["unselected_color_name"] = CURRENT_THEME["highlight_unselected_color"]
    return config

def get_selector_effect_attrs(effect="REVERSE_BLINK", frame=0, speed_factor=10) -> int:
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

def draw_global_selector_line(stdscr, row: int, text: str, is_selected: bool=False, frame: int=0) -> None:
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