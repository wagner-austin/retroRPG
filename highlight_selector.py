# FileName: highlight_selector.py
# version: 1.3 (Now uses separate selected_color_name vs. unselected_color_name)
# Summary: Provides a single, globally configurable highlight/selector system.
# Tags: selector, highlight, effects

import curses
from color_init import color_pairs

# -------------------------------------------------------------------
# 1) GLOBAL HIGHLIGHT CONFIG
# -------------------------------------------------------------------
GLOBAL_HIGHLIGHT_CONFIG = {
    "selected_color_name":   "UI_YELLOW",   # old name, mapped to "yellow_on_black"
    "unselected_color_name": "WHITE_TEXT",  # old name, mapped to "white_on_black"
    "effect_name":           "REVERSE_BLINK",
    "speed_factor":          5,
}

def get_global_selector_config():
    return GLOBAL_HIGHLIGHT_CONFIG

def get_selector_effect_attrs(effect="REVERSE_BLINK", frame=0, speed_factor=10):
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

def draw_global_selector_line(stdscr, row, text, is_selected=False, frame=0):
    config = get_global_selector_config()
    selected_color_name   = config["selected_color_name"]
    unselected_color_name = config["unselected_color_name"]
    effect_name           = config["effect_name"]
    speed_factor          = config["speed_factor"]

    _, w = stdscr.getmaxyx()
    truncated = text[: w - 4]

    try:
        if is_selected:
            attrs = get_selector_effect_attrs(effect=effect_name,
                                              frame=frame,
                                              speed_factor=speed_factor)
            color = curses.color_pair(color_pairs[selected_color_name]) | attrs
        else:
            color = curses.color_pair(color_pairs[unselected_color_name])
        stdscr.addstr(row, 2, truncated, color)
    except curses.error:
        pass