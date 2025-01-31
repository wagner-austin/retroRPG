# FileName: curses_renderer.py
# version: 3.8
#
# Summary: A curses-based in-game renderer implementing IGameRenderer,
#          with partial scrolling as a rendering optimization only.
#          No camera or game logic in this file.
#
# Tags: curses, ui, rendering

import curses
import debug

from engine_interfaces import IGameRenderer

from .curses_color_init import init_colors
from .curses_highlight import get_color_attr
from .curses_utils import safe_addch, safe_addstr, parse_two_color_names
from .curses_common import draw_screen_frame
from .curses_themes import CURRENT_THEME
from scenery_defs import ALL_SCENERY_DEFS, TREE_TRUNK_ID, TREE_TOP_ID
from scenery_main import FLOOR_LAYER, OBJECTS_LAYER, ITEMS_LAYER, ENTITIES_LAYER

class CursesGameRenderer(IGameRenderer):
    """
    Implements IGameRenderer using curses: strictly drawing logic only.
    Partial scrolling is done as a rendering optimization if the camera
    has moved by exactly +1 or -1 row. No camera logic here.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.map_top_offset = 3

        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        curses.curs_set(0)

    def render_scene(self, model, scene_layers):
        """
        Render a scene composed of multiple layers. We'll sort them by z ascending,
        then call a sub-render function for each layer if 'visible' is True.
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
        Actually draw the requested layer_name.
        """
        if layer_name == "background":
            # Use the theme's border color when drawing the frame
            border_col = CURRENT_THEME["border_color"]
            draw_screen_frame(self.stdscr, border_col)

        elif layer_name == "game_world":
            if model:
                self._full_redraw(model)

    def render(self, model):
        # Decide if we can do partial scrolling in Y direction
        dx = getattr(model, "ui_scroll_dx", 0)
        dy = getattr(model, "ui_scroll_dy", 0)

        if model.full_redraw_needed:
            self._full_redraw(model)
            model.full_redraw_needed = False
        else:
            # If camera moved exactly ±1 row in Y (and no X movement),
            # we try partial scroll. Otherwise, just update dirty tiles.
            if dx == 0 and abs(dy) == 1:
                self._partial_scroll(dy, model)
            else:
                self._update_dirty_tiles(model)

        # Reset the scroll deltas
        model.ui_scroll_dx = 0
        model.ui_scroll_dy = 0

        self.stdscr.noutrefresh()
        curses.doupdate()

    def _partial_scroll(self, dy, model):
        """
        Curses-specific partial scrolling optimization when camera moves by ±1 row.
        """
        max_h, max_w = self.stdscr.getmaxyx()
        self.stdscr.setscrreg(self.map_top_offset, max_h - 1)

        try:
            if dy == 1:
                # Scrolling down -> camera moved up by 1
                self.stdscr.scroll(1)
                new_row = model.camera_y + (max_h - self.map_top_offset) - 1
                for col in range(model.camera_x, model.camera_x + max_w):
                    model.dirty_tiles.add((col, new_row))
            elif dy == -1:
                # Scrolling up -> camera moved down by 1
                self.stdscr.scroll(-1)
                new_row = model.camera_y
                for col in range(model.camera_x, model.camera_x + max_w):
                    model.dirty_tiles.add((col, new_row))

        except curses.error:
            model.full_redraw_needed = True

        self.stdscr.setscrreg(0, max_h - 1)
        self._update_dirty_tiles(model)

    def _full_redraw(self, model):
        self.stdscr.clear()
        self._draw_screen_frame()

        # Show either editor info or player's inventory
        if model.context.enable_editor_commands and model.editor_scenery_list:
            sel_def_id = model.editor_scenery_list[model.editor_scenery_index][0]
            self._draw_text(1, 2, f"Editor Mode - Selected: {sel_def_id}")
        else:
            inv_text = (
                f"Inventory: Gold={model.player.gold}, "
                f"Wood={model.player.wood}, Stone={model.player.stone}"
            )
            self._draw_text(1, 2, inv_text)

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
        blank_attr = get_color_attr("white_on_black")
        safe_addch(self.stdscr, sy, sx, " ", blank_attr, clip_borders=True)

        tile_layers = model.placed_scenery.get((wx, wy), None)
        if not tile_layers:
            return

        # Floor
        floor_obj = tile_layers.get(FLOOR_LAYER)
        floor_color_name = "white_on_black"
        if floor_obj:
            info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
            ch = info.get("ascii_char", floor_obj.char)
            floor_color_name = info.get("color_name", "white_on_black")
            floor_attr = get_color_attr(floor_color_name)
            safe_addch(self.stdscr, sy, sx, ch, floor_attr, clip_borders=True)

        # Objects, items, entities
        obj_list = tile_layers.get(OBJECTS_LAYER, []) + \
                   tile_layers.get(ITEMS_LAYER, []) + \
                   tile_layers.get(ENTITIES_LAYER, [])

        for obj in obj_list:
            info = ALL_SCENERY_DEFS.get(obj.definition_id, {})
            ch = info.get("ascii_char", obj.char)
            obj_color_name = info.get("color_name", "white_on_black")

            # If it's specifically TreeTop on the player's tile, handle later
            if obj.definition_id == TREE_TOP_ID and (wx, wy) == (model.player.x, model.player.y):
                continue

            fg_floor, bg_floor = parse_two_color_names(floor_color_name)
            fg_obj, _ = parse_two_color_names(obj_color_name)
            final_color = f"{fg_obj}_on_{bg_floor}"
            attr = get_color_attr(final_color)

            safe_addch(self.stdscr, sy, sx, ch, attr, clip_borders=True)

    def _draw_player_on_top(self, model):
        px = model.player.x - model.camera_x
        py = model.player.y - model.camera_y + self.map_top_offset
        max_h, max_w = self.stdscr.getmaxyx()

        if 0 <= px < max_w and 0 <= py < max_h:
            tile_layers = model.placed_scenery.get((model.player.x, model.player.y), {})
            floor_obj = tile_layers.get(FLOOR_LAYER)
            floor_color_name = "white_on_black"
            if floor_obj:
                finfo = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
                floor_color_name = finfo.get("color_name", "white_on_black")

            fg_floor, bg_floor = parse_two_color_names(floor_color_name)
            player_color = f"white_on_{bg_floor}"
            attr_bold = get_color_attr(player_color, bold=True)
            safe_addch(self.stdscr, py, px, "@", attr_bold, clip_borders=True)

            # Overwrite with trunk/top if present
            objects_list = tile_layers.get(OBJECTS_LAYER, [])
            trunk_tops = [o for o in objects_list if o.definition_id in (TREE_TRUNK_ID, TREE_TOP_ID)]
            for t_obj in trunk_tops:
                info = ALL_SCENERY_DEFS.get(t_obj.definition_id, {})
                ch = info.get("ascii_char", t_obj.char)
                top_color = info.get("color_name", "white_on_black")

                fg_obj, _ = parse_two_color_names(top_color)
                final_color = f"{fg_obj}_on_{bg_floor}"
                trunk_attr = get_color_attr(final_color)
                safe_addch(self.stdscr, py, px, ch, trunk_attr, clip_borders=True)

    def _draw_screen_frame(self):
        draw_screen_frame(self.stdscr)

    def _draw_text(self, row, col, text, color_name=None, bold=False, underline=False):
        """
        Draw text at (row, col). If no color_name given, use CURRENT_THEME["text_color"].
        """
        if color_name is None:
            color_name = CURRENT_THEME["text_color"]
        attr = get_color_attr(color_name, bold=bold, underline=underline)
        safe_addstr(self.stdscr, row, col, text, attr, clip_borders=True)