# FileName: engine_render.py
# version: 3.5 (UI-agnostic now)
# Summary: Keeps shared rendering data but no direct curses calls.
# Tags: engine, rendering, color

RENDER_MODE = "ascii"

# Old color-pair ID -> string mapping
LEGACY_COLOR_MAP = {
    1:  "green_on_black",
    2:  "yellow_on_black",
    3:  "white_on_black",
    4:  "white_on_blue",
    5:  "white_on_green",
    7:  "green_on_white",
    8:  "black_on_yellow",
    12: "yellow_on_black",
    16: "white_on_black",
    17: "red_on_black",
    # etc...
}

# No direct drawing here. All curses calls are in curses_ui.py.