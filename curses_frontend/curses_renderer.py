# FileName: curses_renderer.py
# version: 4.0 (modified to implement new prompt_yes_no and quick_save methods)
#
# Summary: A curses-based in-game renderer implementing IGameRenderer. Renders only the camera region.
#
# Tags: curses, ui, rendering

import curses
#from engine_interfaces import IGameRenderer
from engine_interfaces import IGameRenderer
from .curses_highlight import get_color_attr
from .curses_utils import safe_addch, safe_addstr, parse_two_color_names
from .curses_common import draw_screen_frame
from .where_curses_themes_lives import CURRENT_THEME

# We import the quick-save and yes/no logic from the curses scene:
from .curses_scene_save import perform_quick_save, prompt_yes_no_curses

from scenery_defs import ALL_SCENERY_DEFS, TREE_TRUNK_ID, TREE_TOP_ID
from layer_defs import FLOOR_LAYER, OBJECTS_LAYER, ITEMS_LAYER, ENTITIES_LAYER


class CursesGameRenderer(IGameRenderer):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.map_top_offset = 3
        self.map_side_offset = 0

        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        curses.curs_set(0)

    def get_curses_window(self):
        """
        Provide access to the underlying curses window, in case other logic needs it.
        """
        return self.stdscr

    def get_visible_size(self):
        """
        Overridden to return the actual curses screen size minus any offsets.
        """
        max_h, max_w = self.stdscr.getmaxyx()

        visible_rows = max_h - self.map_top_offset
        if visible_rows < 0:
            visible_rows = 0

        visible_cols = max_w - self.map_side_offset
        return (visible_cols, visible_rows)

    def render_scene(self, model, scene_layers):
        self.stdscr.erase()

        # Draw each layer in ascending z order
        sorted_layers = sorted(scene_layers, key=lambda l: l["z"])
        for layer in sorted_layers:
            if layer.get("visible", True):
                layer_name = layer.get("name", "")
                self._render_layer(layer_name, model)

        self.stdscr.noutrefresh()
        curses.doupdate()

    def _render_layer(self, layer_name, model):
        if layer_name == "background":
            border_col = CURRENT_THEME["border_color"]
            draw_screen_frame(self.stdscr, border_col)
        elif layer_name == "game_world":
            if model:
                self._full_redraw(model)

    def render(self, model):
        dx = getattr(model, "ui_scroll_dx", 0)
        dy = getattr(model, "ui_scroll_dy", 0)

        # If camera moved or a full redraw is requested, redraw everything
        if model.full_redraw_needed or dx != 0 or dy != 0:
            self._full_redraw(model)
            model.full_redraw_needed = False
        else:
            self._update_dirty_tiles(model)

        model.ui_scroll_dx = 0
        model.ui_scroll_dy = 0

        self.stdscr.noutrefresh()
        curses.doupdate()

    def _full_redraw(self, model):
        self.stdscr.clear()
        self._draw_screen_frame()

        # Display either editor info or inventory
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

        for wx in range(model.camera_x, model.camera_x + visible_cols):
            for wy in range(model.camera_y, model.camera_y + visible_rows):
                model.dirty_tiles.add((wx, wy))

        self._update_dirty_tiles(model)

    def _update_dirty_tiles(self, model):
        max_h, max_w = self.stdscr.getmaxyx()

        for (wx, wy) in model.dirty_tiles:
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

        # Render Floor
        floor_obj = tile_layers.get(FLOOR_LAYER)
        floor_color_name = "white_on_black"
        if floor_obj:
            info = ALL_SCENERY_DEFS.get(floor_obj.definition_id, {})
            ch = info.get("ascii_char", floor_obj.char)
            floor_color_name = info.get("color_name", "white_on_black")
            floor_attr = get_color_attr(floor_color_name)
            safe_addch(self.stdscr, sy, sx, ch, floor_attr, clip_borders=True)

        # Render Objects, Items, Entities in that order
        obj_list = (
            tile_layers.get(OBJECTS_LAYER, []) +
            tile_layers.get(ITEMS_LAYER, []) +
            tile_layers.get(ENTITIES_LAYER, [])
        )

        for obj in obj_list:
            info = ALL_SCENERY_DEFS.get(obj.definition_id, {})
            ch = info.get("ascii_char", obj.char)
            obj_color_name = info.get("color_name", "white_on_black")

            # If it's a TreeTop exactly where the player is, skip until player is drawn.
            if obj.definition_id == TREE_TOP_ID and (wx, wy) == (model.player.x, model.player.y):
                continue

            fg_floor, bg_floor = parse_two_color_names(floor_color_name)
            fg_obj, _ = parse_two_color_names(obj_color_name)
            final_color = f"{fg_obj}_on_{bg_floor}"
            attr = get_color_attr(final_color)

            safe_addch(self.stdscr, sy, sx, ch, attr, clip_borders=True)

    def _draw_player_on_top(self, model):
        # Finally render the player in the correct offset
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

            # If there's a tree trunk/top in the same tile, it goes on top of the player
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
        if color_name is None:
            color_name = CURRENT_THEME["text_color"]
        attr = get_color_attr(color_name, bold=bold, underline=underline)
        safe_addstr(self.stdscr, row, col, text, attr, clip_borders=True)

    # -------------------------------------------------------------------------
    # Implement the new UI-agnostic methods from IGameRenderer:
    # -------------------------------------------------------------------------
    def quick_save(self, model):
        """
        Perform a quick-save by delegating to the curses_scene_save logic.
        """
        perform_quick_save(model, self)