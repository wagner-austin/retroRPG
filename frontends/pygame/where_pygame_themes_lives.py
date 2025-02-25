# File: where_pygame_themes_lives.py
#
# version: 1.1
#
# Summary: Holds multiple named theme definitions (colors and ASCII art).
#          Provides a global CURRENT_THEME for the rest of the UI.
#
# Tags: themes, pygame

from .where_pygame_art_lives import (
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
        "border_color":              "blue_on_black",
        "title_color":               "green_on_black",
        "instructions_color":        "white_on_black",
        "text_color":                "white_on_black",
        "ascii_art_color":           "magenta_on_black",
        "highlight_selected_color":  "yellow_on_black",
        "highlight_unselected_color":"white_on_black",
        "prompt_color":              "cyan_on_black",
        "menu_item_color":           "yellow_on_black",
        "confirmation_color":        "white_on_black",
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
        "border_color":              "magenta_on_black",
        "title_color":               "white_on_blue",
        "instructions_color":        "cyan_on_black",
        "text_color":                "yellow_on_black",
        "ascii_art_color":           "white_on_black",
        "highlight_selected_color":  "yellow_on_black",
        "highlight_unselected_color":"white_on_black",
        "prompt_color":              "magenta_on_black",
        "menu_item_color":           "yellow_on_black",
        "confirmation_color":        "white_on_black",
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
    Switches the global CURRENT_THEME to the given theme name.
    Falls back to 'default' if not found.
    """
    global CURRENT_THEME
    CURRENT_THEME = THEMES.get(theme_name, THEMES["default"])