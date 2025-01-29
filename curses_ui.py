# FileName: curses_ui.py
# version: 1.5 (unified map saving/loading UI)
# Summary: All curses-based UI rendering, including map saving or loading screens, partial scroll, etc.
# Tags: curses, ui, rendering

import curses
import debug
import os

from color_init import color_pairs, init_colors
from highlight_selector import get_color_attr, draw_global_selector_line
from curses_utils import safe_addch, safe_addstr, parse_two_color_names
from engine_render import LEGACY_COLOR_MAP, RENDER_MODE
from scenery_defs import ALL_SCENERY_DEFS, TREE_TRUNK_ID, TREE_TOP_ID
from scenery_main import FLOOR_LAYER, OBJECTS_LAYER, ITEMS_LAYER, ENTITIES_LAYER

class CursesUIRenderer:
    """
    A curses front-end that provides:
      - Basic drawing (partial redraw, text, border)
      - Prompt yes/no
      - Display "map list" for saving or loading
      - etc.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        curses.curs_set(0)
        init_colors()

        self.map_top_offset = 3

    def get_input(self):
        return self.stdscr.getch()

    def get_visible_size(self):
        max_h, max_w = self.stdscr.getmaxyx()
        return (max_w, max_h - self.map_top_offset)

    ########################################################################
    # PUBLIC UI METHODS: MAP SAVE/LOAD
    ########################################################################
    def display_map_list_for_save(self):
        """
        Show the "save map" screen. Return either "NEW_FILE", a filename, or "" if canceled.
        """
        maps_dir = "maps"
        if not os.path.isdir(maps_dir):
            os.makedirs(maps_dir, exist_ok=True)

        files = [f for f in os.listdir(maps_dir) if f.endswith(".json")]
        files.sort()

        while True:
            self._draw_save_map_screen()  # Clear & draw background
            max_h, max_w = self.stdscr.getmaxyx()
            row = 10

            if files:
                attr_cyan = get_color_attr("UI_CYAN")
                self._draw_text(row, 2, "Maps (pick a number to overwrite) or 'n' for new, or ENTER to cancel:", "UI_CYAN")
                row += 1
                i = 1
                for filename in files:
                    if row >= max_h - 1:
                        break
                    self._draw_text(row, 2, f"{i}. {filename}", "YELLOW_TEXT")
                    row += 1
                    i += 1
                if row < max_h - 1:
                    self._draw_text(row, 2, "Enter choice or press Enter to cancel:", "UI_CYAN")
                    row += 1
            else:
                self._draw_text(row, 2, "No existing maps. Press 'n' to create new, or Enter to cancel:", "UI_CYAN")
                row += 1

            self.stdscr.refresh()

            if row < max_h:
                selection_bytes = self.stdscr.getstr(row, 2, 20)
                if not selection_bytes:
                    return ""
                selection = selection_bytes.decode('utf-8').strip()
                if not selection:
                    return ""
                if selection.lower() == 'n':
                    return "NEW_FILE"
                elif selection.lower() == 'v':
                    debug.toggle_debug()
                    continue
                elif selection.isdigit():
                    idx = int(selection) - 1
                    if 0 <= idx < len(files):
                        return files[idx]
            else:
                return ""

    def prompt_for_filename(self, prompt_text: str):
        """
        Let user type a new filename. Return the typed filename or "" if none.
        """
        self._draw_save_map_screen()
        max_h, max_w = self.stdscr.getmaxyx()
        row = 10
        if row < max_h - 1:
            attr_cyan = get_color_attr("UI_CYAN")
            safe_addstr(self.stdscr, row, 2, prompt_text, attr_cyan, clip_borders=True)
            self.stdscr.refresh()
            curses.echo()
            filename_bytes = self.stdscr.getstr(row, 2 + len(prompt_text) + 1, 30)
            curses.noecho()
            if filename_bytes:
                return filename_bytes.decode('utf-8', errors='ignore').strip()
        return ""

    def notify_overwrite(self, filename):
        """
        Minimally inform the user we overwrote 'filename'.
        E.g., we can show a short message or do a nap.
        """
        max_h, max_w = self.stdscr.getmaxyx()
        row = max_h - 2
        msg = f"Overwrote {filename}. Press any key..."
        attr = get_color_attr("WHITE_TEXT")
        safe_addstr(self.stdscr, row, 0, " " * (max_w - 1), attr, clip_borders=False)
        safe_addstr(self.stdscr, row, 2, msg, attr, clip_borders=False)
        self.stdscr.refresh()
        self.stdscr.nodelay(False)
        self.stdscr.getch()
        self.stdscr.nodelay(True)

    ########################################################################
    # For a future "load map" screen, you can do similarly:
    # def display_map_list(self): ...
    ########################################################################

    ########################################################################
    # The rest is the same partial-scroll rendering code as before
    ########################################################################

    def on_camera_move(self, dx, dy, model):
        if abs(dx) > 1 or abs(dy) > 1:
            return
        if dx == 0 and dy == 0:
            return
        self._partial_scroll(dx, dy, model)

    def full_redraw(self, model):
        self.stdscr.clear()
        self._draw_screen_frame("UI_CYAN")

        if model.context.enable_editor_commands and model.editor_scenery_list:
            sel_def_id = model.editor_scenery_list[model.editor_scenery_index][0]
            self._draw_text(1, 2, f"Editor Mode - Selected: {sel_def_id}", "WHITE_TEXT")
        else:
            inv_text = (
                f"Inventory: Gold={model.player.gold}, "
                f"Wood={model.player.wood}, Stone={model.player.stone}"
            )
            self._draw_text(1, 2, inv_text, "WHITE_TEXT")

        max_h, max_w = self.stdscr.getmaxyx()
        visible_cols = max_w
        visible_rows = max_h - self.map_top_offset
        for wx in range(model.camera_x, min(model.camera_x + visible_cols, model.world_width)):
            for wy in range(model.camera_y, min(model.camera_y + visible_rows, model.world_height)):
                model.dirty_tiles.add((wx, wy))

        self.update_dirty_tiles(model)

    def update_dirty_tiles(self, model):
        self._update_partial_tiles_in_view(model)
        self._draw_player_on_top(model)
        self.stdscr.noutrefresh()
        curses.doupdate()

    def prompt_yes_no(self, question: str) -> bool:
        max_h, max_w = self.stdscr.getmaxyx()
        prompt_row = max_h - 2
        safe_addstr(self.stdscr, prompt_row, 0, " " * (max_w - 1), 0, clip_borders=False)
        safe_addstr(self.stdscr, prompt_row, 2, question, 0, clip_borders=False)
        self.stdscr.refresh()

        self.stdscr.nodelay(False)
        while True:
            c = self.stdscr.getch()
            if c in (ord('y'), ord('Y')):
                self.stdscr.nodelay(True)
                return True
            elif c in (ord('n'), ord('N'), ord('q'), 27):
                self.stdscr.nodelay(True)
                return False

    def _partial_scroll(self, dx, dy, model):
        max_h, max_w = self.stdscr.getmaxyx()
        visible_cols = max_w
        visible_rows = max_h - self.map_top_offset

        def fallback_reblit():
            for row in range(model.camera_y, model.camera_y + visible_rows):
                for col in range(model.camera_x, model.camera_x + visible_cols):
                    model.dirty_tiles.add((col, row))

        if dx != 0:
            fallback_reblit()
            return
        if abs(dy) > 1:
            fallback_reblit()
            return

        self.stdscr.setscrreg(self.map_top_offset, max_h - 1)
        try:
            if dy == 1:
                self.stdscr.scroll(1)
                new_row = model.camera_y + visible_rows - 1
                for col in range(model.camera_x, model.camera_x + visible_cols):
                    model.dirty_tiles.add((col, new_row))
            elif dy == -1:
                self.stdscr.scroll(-1)
                new_row = model.camera_y
                for col in range(model.camera_x, model.camera_x + visible_cols):
                    model.dirty_tiles.add((col, new_row))
        except curses.error:
            fallback_reblit()

        self.stdscr.setscrreg(0, max_h - 1)

    def _update_partial_tiles_in_view(self, model):
        max_h, max_w = self.stdscr.getmaxyx()
        from highlight_selector import get_color_attr
        for (wx, wy) in model.dirty_tiles:
            if 0 <= wx < model.world_width and 0 <= wy < model.world_height:
                sx = wx - model.camera_x
                sy = wy - model.camera_y + self.map_top_offset
                if 0 <= sx < max_w and 0 <= sy < max_h:
                    blank_attr = get_color_attr("white_on_black")
                    safe_addch(self.stdscr, sy, sx, " ", blank_attr, clip_borders=True)

                    tile_layers = model.placed_scenery.get((wx, wy), None)
                    if not tile_layers:
                        continue

                    floor_obj = tile_layers.get(FLOOR_LAYER)
                    floor_fg_index = 0
                    if floor_obj:
                        self._draw_floor(floor_obj, sx, sy)
                        info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
                        floor_fg_index = info.get("ascii_color", floor_obj.color_pair)

                    obj_list = tile_layers.get(OBJECTS_LAYER, [])
                    for obj in obj_list:
                        if obj.definition_id in (TREE_TRUNK_ID, TREE_TOP_ID):
                            if (wx, wy) == (model.player.x, model.player.y):
                                continue
                        self._draw_object(obj, sx, sy, floor_fg_index)

                    for it in tile_layers.get(ITEMS_LAYER, []):
                        self._draw_object(it, sx, sy, floor_fg_index)

                    for ent in tile_layers.get(ENTITIES_LAYER, []):
                        self._draw_object(ent, sx, sy, floor_fg_index)

    def _draw_floor(self, floor_obj, sx, sy):
        info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
        ch = info.get("ascii_char", floor_obj.char)
        fg_index = info.get("ascii_color", floor_obj.color_pair)
        base_color = LEGACY_COLOR_MAP.get(fg_index, "white_on_black")
        floor_attr = get_color_attr(base_color)
        safe_addch(self.stdscr, sy, sx, ch, floor_attr, clip_borders=True)

    def _draw_object(self, obj, sx, sy, floor_fg_index):
        from highlight_selector import get_color_attr
        info = ALL_SCENERY_DEFS.get(obj.definition_id, {})
        ch = info.get("ascii_char", obj.char)
        obj_fg_index = info.get("ascii_color", obj.color_pair)
        if obj.definition_id == TREE_TOP_ID:
            color_name = LEGACY_COLOR_MAP.get(obj_fg_index, "green_on_black")
            attr = get_color_attr(color_name)
            safe_addch(self.stdscr, sy, sx, ch, attr, clip_borders=True)
            return

        floor_base = LEGACY_COLOR_MAP.get(floor_fg_index, "white_on_black")
        fg_part, bg_part = parse_two_color_names(floor_base)

        obj_color_name = LEGACY_COLOR_MAP.get(obj_fg_index, "white_on_black")
        real_fg, _ = parse_two_color_names(obj_color_name)
        final_color = f"{real_fg}_on_{bg_part}"
        attr = get_color_attr(final_color)
        safe_addch(self.stdscr, sy, sx, ch, attr, clip_borders=True)

    def _draw_player_on_top(self, model):
        px = model.player.x - model.camera_x
        py = model.player.y - model.camera_y + self.map_top_offset
        max_h, max_w = self.stdscr.getmaxyx()
        if 0 <= px < max_w and 0 <= py < max_h:
            tile_layers = model.placed_scenery.get((model.player.x, model.player.y), {})
            floor_obj = tile_layers.get(FLOOR_LAYER)
            floor_fg_index = 0
            if floor_obj:
                floor_info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
                floor_fg_index = floor_info.get("ascii_color", floor_obj.color_pair)
            floor_base = LEGACY_COLOR_MAP.get(floor_fg_index, "white_on_black")
            fg_part, bg_part = parse_two_color_names(floor_base)

            color_name = f"white_on_{bg_part}"
            attr_bold = get_color_attr(color_name, bold=True)
            safe_addch(self.stdscr, py, px, "@", attr_bold, clip_borders=True)

            objects_list = tile_layers.get(OBJECTS_LAYER, [])
            trunk_tops = [o for o in objects_list if o.definition_id in (TREE_TRUNK_ID, TREE_TOP_ID)]
            if trunk_tops:
                for t_obj in trunk_tops:
                    info = ALL_SCENERY_DEFS.get(t_obj.definition_id, {})
                    ch = info.get("ascii_char", t_obj.char)
                    fg_index = info.get("ascii_color", t_obj.color_pair)
                    base_col = LEGACY_COLOR_MAP.get(fg_index, "white_on_black")
                    obj_fg, _ = parse_two_color_names(base_col)
                    final_col = f"{obj_fg}_on_white"
                    attr = get_color_attr(final_col)
                    safe_addch(self.stdscr, py, px, ch, attr, clip_borders=True)

    def _draw_screen_frame(self, color_name="UI_CYAN"):
        self._draw_border(color_name)
        if debug.DEBUG_CONFIG["enabled"]:
            max_h, max_w = self.stdscr.getmaxyx()
            label = "Debug mode: On"
            col = max_w - len(label) - 2
            dbg_attr = get_color_attr("WHITE_TEXT")
            safe_addstr(self.stdscr, 0, col, label, dbg_attr, clip_borders=False)

    def _draw_border(self, color_name):
        from highlight_selector import get_color_attr
        h, w = self.stdscr.getmaxyx()
        if h < 3 or w < 3:
            return
        border_attr = get_color_attr(color_name)
        for x in range(w):
            safe_addch(self.stdscr, 0, x, curses.ACS_HLINE, border_attr, clip_borders=False)
        safe_addch(self.stdscr, 0, 0, curses.ACS_ULCORNER, border_attr, clip_borders=False)
        safe_addch(self.stdscr, 0, w - 1, curses.ACS_URCORNER, border_attr, clip_borders=False)

        for x in range(w):
            safe_addch(self.stdscr, h - 1, x, curses.ACS_HLINE, border_attr, clip_borders=False)
        safe_addch(self.stdscr, h - 1, 0, curses.ACS_LLCORNER, border_attr, clip_borders=False)
        safe_addch(self.stdscr, h - 1, w - 1, curses.ACS_LRCORNER, border_attr, clip_borders=False)

        for y in range(1, h - 1):
            safe_addch(self.stdscr, y, 0, curses.ACS_VLINE, border_attr, clip_borders=False)
            safe_addch(self.stdscr, y, w - 1, curses.ACS_VLINE, border_attr, clip_borders=False)

    def _draw_text(self, row, col, text, color_name, bold=False, underline=False):
        from highlight_selector import get_color_attr
        attr = get_color_attr(color_name, bold=bold, underline=underline)
        safe_addstr(self.stdscr, row, col, text, attr, clip_borders=True)

    def _draw_save_map_screen(self):
        """
        Clears screen and draws a "Save Map" title. Called by display_map_list_for_save or prompt_for_filename.
        """
        self.stdscr.clear()
        self._draw_screen_frame("UI_CYAN")
        self._draw_text(1, 2, "Save Map", "UI_MAGENTA")

def run_game_with_curses(stdscr, context, model, engine_main_func):
    renderer = CursesUIRenderer(stdscr)
    def input_func():
        return renderer.get_input()
    engine_main_func(model, context, input_func, renderer)