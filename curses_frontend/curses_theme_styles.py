# FileName: curses_theme_styles.py
# version: 1.2
# Summary: Provides a centralized theming/border styling system for RetroRPG,
#          now using ASCII-only borders, unified across scenes.
# Tags: theme, style, border, curses

import curses

##############################################################################
# THEME DICTIONARY
##############################################################################
THEME = {
    "background":       "black_on_black",    # default fallback background color
    "title_color":      "white_on_black",    # color for titles
    "text_color":       "white_on_black",    # main text color
    "instruction_color":"magenta_on_black",  # instructions / footers
}

##############################################################################
# BORDER_STYLES (ASCII-only)
# We define two distinct ones: "home_box" and "white_box"
##############################################################################
BORDER_STYLES = {
    "home_box": {
        "color_name":        "WHITE_TEXT",  # or any valid color alias from curses_color_init
        "corner_tl":         "+",
        "corner_tr":         "+",
        "corner_bl":         "+",
        "corner_br":         "+",
        "line_horizontal":   "-",
        "line_vertical":     "|",
    },
    "white_box": {
        "color_name":        "WHITE_TEXT",
        "corner_tl":         "+",
        "corner_tr":         "+",
        "corner_bl":         "+",
        "corner_br":         "+",
        "line_horizontal":   "-",
        "line_vertical":     "|",
    },
}

##############################################################################
# SCENE_BORDER_MAP
# Which border style to use for each scene name.
##############################################################################
SCENE_BORDER_MAP = {
    "HOME":     "home_box",
    "SETTINGS": "white_box",
    "LOAD":     "white_box",
    "SAVE":     "white_box",
    "GAME":     "white_box",
}

##############################################################################
# OPTIONAL PER-SCENE OVERRIDES
# If you want certain scenes to override the default THEME keys.
##############################################################################
SCENE_THEME_OVERRIDES = {
    "HOME": {
        "background":  "black_on_white",
        # "title_color": "white_on_red",
    },
    "SETTINGS": {
        "title_color": "white_on_magenta",
    },
    # e.g., "LOAD" or "SAVE" could override other aspects if desired.
}