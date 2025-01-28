# FileName: highlight_selector.py
# version: 1.0
# Summary: Provides robust, modular selector highlight functionality (color, blink, glow, flash, shimmer, etc.)
#          for easy usage across different UI screens.
# Tags: selector, highlight, effects

import curses
from color_init import color_pairs

def get_selector_effect_attrs(effect="REVERSE_BLINK", frame=0):
    """
    Returns a curses attribute (or combination) for the desired selector effect.
    Some effects may cycle color or attributes across frames.
    The 'frame' parameter can be used by callers to animate over time.
    
    Available example effects:
      - "NONE"
      - "REVERSE"
      - "BLINK"
      - "REVERSE_BLINK"
      - "FLASH"   (simple demonstration: toggles between normal/reverse every ~10 frames)
      - "GLOW"    (simple demonstration: toggles between bold and normal every ~10 frames)
      - "SHIMMER" (simple demonstration: toggles blink+bold vs. normal)
    """
    if effect == "NONE":
        return curses.A_NORMAL
    elif effect == "REVERSE":
        return curses.A_REVERSE
    elif effect == "BLINK":
        return curses.A_BLINK
    elif effect == "REVERSE_BLINK":
        return curses.A_REVERSE | curses.A_BLINK
    elif effect == "FLASH":
        # Example: alternate every 10 frames
        if (frame // 10) % 2 == 0:
            return curses.A_REVERSE
        else:
            return curses.A_NORMAL
    elif effect == "GLOW":
        # Example: alternate every 10 frames
        if (frame // 10) % 2 == 0:
            return curses.A_BOLD
        else:
            return curses.A_NORMAL
    elif effect == "SHIMMER":
        # Example: alternate every 10 frames
        if (frame // 10) % 2 == 0:
            return curses.A_BOLD | curses.A_BLINK
        else:
            return curses.A_NORMAL
    else:
        # Default fallback
        return curses.A_REVERSE


def draw_selectable_line(stdscr, row, text, is_selected=False,
                         color_name="UI_YELLOW", effect="REVERSE_BLINK", frame=0):
    """
    Draws a single line with optional highlight/selector effect.
    The 'frame' param can be used to vary effect over time (e.g., shimmer or glow).
    """
    _, w = stdscr.getmaxyx()
    truncated = text[:w - 4]  # margin to avoid right-edge curses errors
    try:
        if is_selected:
            attrs = get_selector_effect_attrs(effect, frame=frame)
            color = curses.color_pair(color_pairs[color_name]) | attrs
        else:
            color = curses.color_pair(color_pairs[color_name])
        stdscr.addstr(row, 2, truncated, color)
    except curses.error:
        pass
