# FileName: highlight_selector.py
# version: 1.3 (Now uses separate selected_color_name vs. unselected_color_name)
# Summary: Provides a single, globally configurable highlight/selector system.
#          All UI menus call draw_global_selector_line(), which references
#          GLOBAL_HIGHLIGHT_CONFIG for highlight color, effect type, and speed factor.
# Tags: selector, highlight, effects

import curses
from color_init import color_pairs

# -------------------------------------------------------------------
# 1) GLOBAL HIGHLIGHT CONFIG
#    Now we have separate colors for selected vs. unselected lines,
#    so changing highlight won't force normal lines to also share it.
# -------------------------------------------------------------------
GLOBAL_HIGHLIGHT_CONFIG = {
    "selected_color_name":   "UI_YELLOW",  # color pair for highlighted lines
    "unselected_color_name": "WHITE_TEXT", # color pair for normal lines in selectable lists
    "effect_name":           "REVERSE_BLINK",  # "NONE", "REVERSE", "BLINK", "FLASH", "SHIMMER", etc.
    "speed_factor":          5,               # bigger => slower animation toggles
}


def get_global_selector_config():
    """
    Returns a dictionary with 'selected_color_name', 'unselected_color_name',
    'effect_name', 'speed_factor'.
    Modify GLOBAL_HIGHLIGHT_CONFIG to change them in one place.
    """
    return GLOBAL_HIGHLIGHT_CONFIG


def get_selector_effect_attrs(effect="REVERSE_BLINK", frame=0, speed_factor=10):
    """
    Returns curses attribute(s) for the desired effect, using (frame // speed_factor) % 2
    for toggling. For example, 'SHIMMER' might alternate every few frames.
    """
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
        # Alternates every speed_factor frames between REVERSE and NORMAL
        return curses.A_REVERSE if toggle_state == 0 else curses.A_NORMAL
    elif effect == "GLOW":
        # Alternates every speed_factor frames between BOLD and NORMAL
        return curses.A_BOLD if toggle_state == 0 else curses.A_NORMAL
    elif effect == "SHIMMER":
        # Alternates every speed_factor frames between BOLD+BLINK and NORMAL
        return (curses.A_BOLD | curses.A_BLINK) if toggle_state == 0 else curses.A_NORMAL

    # Fallback
    return curses.A_REVERSE


def draw_global_selector_line(stdscr, row, text, is_selected=False, frame=0):
    """
    Draws a line with highlight if 'is_selected=True'. 
    The highlight color/effect/speed come from GLOBAL_HIGHLIGHT_CONFIG.
    If not selected, we use the 'unselected_color_name' from the config.
    'frame' is the current loop iteration, used for animated effects.
    """
    config = get_global_selector_config()
    selected_color_name   = config["selected_color_name"]
    unselected_color_name = config["unselected_color_name"]
    effect_name           = config["effect_name"]
    speed_factor          = config["speed_factor"]

    _, w = stdscr.getmaxyx()
    truncated = text[:w - 4]  # avoid right-edge errors

    try:
        if is_selected:
            # Use highlight color, plus effect
            attrs = get_selector_effect_attrs(effect=effect_name,
                                              frame=frame,
                                              speed_factor=speed_factor)
            color = curses.color_pair(color_pairs[selected_color_name]) | attrs
        else:
            # Use normal text color
            color = curses.color_pair(color_pairs[unselected_color_name])

        stdscr.addstr(row, 2, truncated, color)
    except curses.error:
        pass