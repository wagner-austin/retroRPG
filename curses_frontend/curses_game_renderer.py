# FileName: curses_game_renderer.py
# version: 4.2 (modified to delegate inventory display to curses_scene_inventory and to call draw_editor_overlay from curses_scene_editor)
#
# Summary: A curses-based in-game renderer implementing IGameRenderer. Renders only the camera region.
#
# Tags: curses, ui, rendering

import curses
from engine_interfaces import IGameRenderer

from .curses_selector_highlight import get_color_attr
from .curses_utils import safe_addstr
from .curses_common import draw_screen_frame
from .where_curses_themes_lives import CURRENT_THEME

# The tile-drawing logic is in curses_tile_drawing.py
from .curses_tile_drawing import draw_single_tile, draw_player_on_top

# Import the inventory summary drawer
from .curses_scene_inventory import draw_inventory_summary

# Import the editor overlay drawer
from .curses_scene_editor import draw_editor_overlay


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


    def render_scene(self, scene, dt=0, context=None):
        """
        Renders a Scene object that provides .get_layers().
        :param scene: a Scene instance containing SceneLayer objects.
        :param dt: a frame counter or time delta.
        :param context: the game model or other relevant data.
        """
        self.stdscr.erase()

        # 1) Retrieve layers from the scene.
        layers = scene.get_layers()  # This returns a list of SceneLayer objects.

        # 2) Sort layers by their z_index.
        layers_sorted = sorted(layers, key=lambda layer: layer.z_index)

        # 3) Draw each layer (lowest z_index drawn first).
        for layer in layers_sorted:
            layer.draw(self, dt, context)

        # 4) Refresh the screen.
        self.stdscr.noutrefresh()
        curses.doupdate()

    def _render_layer(self, layer_name, model):
        """
        By default, we only handle 'background' or 'game_world' here.
        """
        if layer_name == "background":
            border_col = CURRENT_THEME["border_color"]
            draw_screen_frame(self.stdscr, border_col)
        elif layer_name == "game_world":
            if model:
                self._full_redraw(model)

    def render(self, model):
        """
        Called each frame to render the current game state, possibly partially.
        """
        dx = getattr(model, "ui_scroll_dx", 0)
        dy = getattr(model, "ui_scroll_dy", 0)

        # If camera moved or a full redraw is requested, do a full update
        if model.full_redraw_needed or dx != 0 or dy != 0:
            self._full_redraw(model)
            model.full_redraw_needed = False
        else:
            self._update_dirty_tiles(model)

        # Reset the scroll deltas
        model.ui_scroll_dx = 0
        model.ui_scroll_dy = 0

        self.stdscr.noutrefresh()
        curses.doupdate()

    def _full_redraw(self, model):
        self.stdscr.clear()
        self._draw_screen_frame()

        # New approach: delegate the editor overlay to curses_scene_editor,
        # and if it's not in editor mode, show inventory summary
        draw_editor_overlay(self.stdscr, model)
        if not (model.context.enable_editor_commands and model.editor_scenery_list):
            draw_inventory_summary(self.stdscr, model, row=1, col=2)

        max_h, max_w = self.stdscr.getmaxyx()
        visible_cols = max_w
        visible_rows = max_h - self.map_top_offset

        # Mark every tile in the visible region as dirty
        for wx in range(model.camera_x, model.camera_x + visible_cols):
            for wy in range(model.camera_y, model.camera_y + visible_rows):
                model.dirty_tiles.add((wx, wy))

        self._update_dirty_tiles(model)

    def _update_dirty_tiles(self, model):
        """
        Re-draw only the tiles in model.dirty_tiles, then draw the player on top.
        """
        max_h, max_w = self.stdscr.getmaxyx()
        blank_attr = get_color_attr("white_on_black")

        for (wx, wy) in model.dirty_tiles:
            sx = wx - model.camera_x
            sy = wy - model.camera_y + self.map_top_offset
            if 0 <= sx < max_w and 0 <= sy < max_h:
                # Paint this tile
                draw_single_tile(self.stdscr, wx, wy, sx, sy, model, blank_attr)

        # After drawing all tiles, draw the player on top
        draw_player_on_top(self.stdscr, model, self.map_top_offset)

    def _draw_screen_frame(self):
        draw_screen_frame(self.stdscr)

    def _draw_text(self, row, col, text, color_name=None, bold=False, underline=False):
        if color_name is None:
            color_name = CURRENT_THEME["text_color"]
        attr = get_color_attr(color_name, bold=bold, underline=underline)
        safe_addstr(self.stdscr, row, col, text, attr, clip_borders=True)