# FileName: curses_themes.py
#
# version: 1.1
#
# Summary: Holds multiple named theme definitions (colors and ASCII art).
#          Provides a global CURRENT_THEME for the rest of the UI.
#
# Tags: themes, curses

from .curses_art_skins import (
    HEADER_ART,
    LOADING_ART,
    HOMESCREEN_ART,
    DECORATION,
    BANNER,
    BORDERS,
    MAIN_MENU_ART,
    CROCODILE
)

THEMES = {
    "default": {
        "border_color":              "UI_CYAN",
        "title_color":               "UI_WHITE_ON_BLUE",
        "instructions_color":        "UI_MAGENTA",
        "text_color":                "YELLOW_TEXT",
        "ascii_art_color":           "ASCII_ART",

        "highlight_selected_color":   "YELLOW_TEXT",
        "highlight_unselected_color": "WHITE_TEXT",

        # Added keys to handle previously hard-coded colors:
        "prompt_color":        "UI_CYAN",
        "menu_item_color":     "YELLOW_TEXT",
        "confirmation_color":  "WHITE_TEXT",

        "header_art":      HEADER_ART,
        "loading_art":     LOADING_ART,
        "homescreen_art":  HOMESCREEN_ART,
        "decoration_art":  DECORATION,
        "banner_art":      BANNER,
        "borders_art":     BORDERS,
        "main_menu_art":   MAIN_MENU_ART,
        "crocodile_art":   CROCODILE,
    },

    "dark": {
        "border_color":              "UI_MAGENTA",
        "title_color":               "UI_WHITE_ON_BLUE",
        "instructions_color":        "UI_CYAN",
        "text_color":                "YELLOW_TEXT",
        "ascii_art_color":           "ASCII_ART",

        "highlight_selected_color":   "YELLOW_TEXT",
        "highlight_unselected_color": "WHITE_TEXT",

        # Same added keys for a consistent dictionary:
        "prompt_color":        "UI_MAGENTA",
        "menu_item_color":     "YELLOW_TEXT",
        "confirmation_color":  "WHITE_TEXT",

        "header_art":      HEADER_ART,
        "loading_art":     LOADING_ART,
        "homescreen_art":  HOMESCREEN_ART,
        "decoration_art":  DECORATION,
        "banner_art":      BANNER,
        "borders_art":     BORDERS,
        "main_menu_art":   MAIN_MENU_ART,
        "crocodile_art":   CROCODILE,
    },
}

CURRENT_THEME = THEMES["default"]

def set_theme(theme_name: str):
    """
    Switch the global CURRENT_THEME to a different named theme.
    Fallbacks to 'default' if not found.
    """
    global CURRENT_THEME
    if theme_name in THEMES:
        CURRENT_THEME = THEMES[theme_name]
    else:
        CURRENT_THEME = THEMES["default"]