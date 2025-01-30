# FileName: curses_renderer.py
#
# version: 3.6
#
# Summary: A curses-based in-game renderer implementing IGameRenderer,
#          plus a new layered render_scene(...) approach for menus or overlays.
#
# Tags: curses, ui, rendering

import curses
import debug
from interfaces import IGameRenderer
from .curses_color_init import init_colors, color_pairs
from .curses_highlight import get_color_attr
from .curses_utils import safe_addch, safe_addstr, parse_two_color_names
from .curses_common import draw_screen_frame
from engine_render import LEGACY_COLOR_MAP
from scenery_defs import ALL_SCENERY_DEFS, TREE_TRUNK_ID, TREE_TOP_ID
from scenery_main import FLOOR_LAYER, OBJECTS_LAYER, ITEMS_LAYER, ENTITIES_LAYER

class CursesGameRenderer(IGameRenderer):
    """
    Implements IGameRenderer using curses: handles rendering the game world,
    partial or full redraw, etc.
    Also provides a 'render_scene(...)' method to draw layered scenes (menus, overlays).
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.map_top_offset = 3

        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        curses.curs_set(0)
        init_colors()

    ########################################################################
    # 1) NEW: LAYERED SCENE RENDERING
    ########################################################################

    def render_scene(self, model, scene_layers):
        """
        Render a scene composed of multiple layers, each with:
            {
              "name": "some_name",
              "visible": True/False,
              "z": <number>
            }

        We'll sort them by z ascending, then call a sub-render function
        for each layer if 'visible' is True.

        If your scene does not need the 'model', pass None, or add some data as needed.
        """
        self.stdscr.erase()

        # Sort by z, then draw
        sorted_layers = sorted(scene_layers, key=lambda l: l["z"])
        for layer in sorted_layers:
            if layer.get("visible", True):
                layer_name = layer.get("name", "")
                self._render_layer(layer_name, model)

        self.stdscr.noutrefresh()
        curses.doupdate()

    def _render_layer(self, layer_name, model):
        """
        Actually draw the requested layer_name. For a real game, you could
        implement dictionary-based dispatch:
          if layer_name == "background": ...
          elif layer_name == "art_layer": ...
          elif layer_name == "game_world": ...
        etc.

        For demonstration, let's do a few placeholders or call existing logic if relevant.
        """
        if layer_name == "background":
            draw_screen_frame(self.stdscr, "UI_CYAN")

        elif layer_name == "game_world":
            # If we want to reuse the existing logic for in-game rendering:
            if model:
                self._full_redraw(model)

        elif layer_name == "title_and_art":
            # Possibly draw some ASCII art from model or a known constant
            pass

        elif layer_name == "menu_overlay":
            # e.g., draw menu text, highlight, etc.
            pass

        # etc.  This is purely an example.

    ########################################################################
    # 2) CLASSIC GAME RENDERING (used during normal gameplay)
    ########################################################################

    def render(self, model):
        if model.full_redraw_needed:
            self._full_redraw(model)
            model.full_redraw_needed = False
        else:
            self._update_dirty_tiles(model)

        self.stdscr.noutrefresh()
        curses.doupdate()

    def on_camera_move(self, dx, dy, model):
        if abs(dx) > 0 or abs(dy) > 1:
            model.full_redraw_needed = True
            return

        max_h, max_w = self.stdscr.getmaxyx()
        self.stdscr.setscrreg(self.map_top_offset, max_h - 1)

        try:
            if dy == 1:
                self.stdscr.scroll(1)
                new_row = model.camera_y + (max_h - self.map_top_offset) - 1
                for col in range(model.camera_x, model.camera_x + max_w):
                    model.dirty_tiles.add((col, new_row))
            elif dy == -1:
                self.stdscr.scroll(-1)
                new_row = model.camera_y
                for col in range(model.camera_x, model.camera_x + max_w):
                    model.dirty_tiles.add((col, new_row))
        except curses.error:
            model.full_redraw_needed = True

        self.stdscr.setscrreg(0, max_h - 1)

    def prompt_yes_no(self, question: str) -> bool:
        """
        A simple curses-based yes/no prompt at the bottom row, returning bool.
        """
        max_h, max_w = self.stdscr.getmaxyx()
        row = max_h - 2
        safe_addstr(self.stdscr, row, 0, " " * (max_w - 1), 0, clip_borders=False)
        safe_addstr(self.stdscr, row, 2, question, 0, clip_borders=False)
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

    def get_curses_window(self):
        return self.stdscr

    ########################################################################
    # 3) INTERNAL GAME RENDER UTILS
    ########################################################################

    def _full_redraw(self, model):
        self.stdscr.clear()
        self._draw_screen_frame()

        # Show either editor info or player's inventory
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

        self._update_dirty_tiles(model)

    def _update_dirty_tiles(self, model):
        max_h, max_w = self.stdscr.getmaxyx()
        for (wx, wy) in model.dirty_tiles:
            if 0 <= wx < model.world_width and 0 <= wy < model.world_height:
                sx = wx - model.camera_x
                sy = wy - model.camera_y + self.map_top_offset
                if 0 <= sx < max_w and 0 <= sy < max_h:
                    self._draw_single_tile(wx, wy, sx, sy, model)

        self._draw_player_on_top(model)

    def _draw_single_tile(self, wx, wy, sx, sy, model):
        # clear background first
        blank_attr = get_color_attr("white_on_black")
        safe_addch(self.stdscr, sy, sx, " ", blank_attr, clip_borders=True)

        tile_layers = model.placed_scenery.get((wx, wy), None)
        if not tile_layers:
            return

        floor_obj = tile_layers.get(FLOOR_LAYER)
        floor_fg_index = 0
        if floor_obj:
            floor_fg_index = self._draw_floor(floor_obj, sx, sy)

        # Draw objects
        for obj in tile_layers.get(OBJECTS_LAYER, []):
            if obj.definition_id in (TREE_TRUNK_ID, TREE_TOP_ID):
                # skip if same tile as player
                if (wx, wy) == (model.player.x, model.player.y):
                    continue
            self._draw_object(obj, sx, sy, floor_fg_index)

        # Draw items
        for it in tile_layers.get(ITEMS_LAYER, []):
            self._draw_object(it, sx, sy, floor_fg_index)

        # Draw entities
        for ent in tile_layers.get(ENTITIES_LAYER, []):
            self._draw_object(ent, sx, sy, floor_fg_index)

    def _draw_floor(self, floor_obj, sx, sy):
        info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
        ch = info.get("ascii_char", floor_obj.char)
        fg_index = info.get("ascii_color", floor_obj.color_pair)
        base_color = LEGACY_COLOR_MAP.get(fg_index, "white_on_black")
        floor_attr = get_color_attr(base_color)
        safe_addch(self.stdscr, sy, sx, ch, floor_attr, clip_borders=True)
        return fg_index

    def _draw_object(self, obj, sx, sy, floor_fg_index):
        info = ALL_SCENERY_DEFS.get(obj.definition_id, {})
        ch = info.get("ascii_char", obj.char)
        obj_fg_index = info.get("ascii_color", obj.color_pair)

        # If it's a tree top on the player's tile, we might skip or handle differently
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
                info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
                floor_fg_index = info.get("ascii_color", floor_obj.color_pair)
            floor_base = LEGACY_COLOR_MAP.get(floor_fg_index, "white_on_black")
            fg_part, bg_part = parse_two_color_names(floor_base)

            color_name = f"white_on_{bg_part}"
            attr_bold = get_color_attr(color_name, bold=True)
            safe_addch(self.stdscr, py, px, "@", attr_bold, clip_borders=True)

            # If there's a trunk/top in the same tile, it might appear over the player
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
                    trunk_attr = get_color_attr(final_col)
                    safe_addch(self.stdscr, py, px, ch, trunk_attr, clip_borders=True)

    def _draw_screen_frame(self):
        draw_screen_frame(self.stdscr)

    def _draw_text(self, row, col, text, color_name, bold=False, underline=False):
        from .curses_highlight import get_color_attr
        attr = get_color_attr(color_name, bold=bold, underline=underline)
        safe_addstr(self.stdscr, row, col, text, attr, clip_borders=True)