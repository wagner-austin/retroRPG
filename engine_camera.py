# FileName: engine_camera.py
# version: 2.6
# Summary: Implements camera logic with partial scrolling. Now uses safe_addstr.
# Tags: engine, camera, scrolling

import curses
from curses_utils import safe_addstr, safe_addch
from typing import Tuple

def update_camera_with_deadzone(player_x: int, player_y: int,
                                camera_x: int, camera_y: int,
                                visible_cols: int, visible_rows: int,
                                world_width: int, world_height: int,
                                dead_zone: int = 2) -> Tuple[int, int]:
    screen_px = player_x - camera_x
    screen_py = player_y - camera_y

    if screen_px < dead_zone:
        camera_x -= (dead_zone - screen_px)
    elif screen_px > (visible_cols - dead_zone - 1):
        camera_x += (screen_px - (visible_cols - dead_zone - 1))

    if screen_py < dead_zone:
        camera_y -= (dead_zone - screen_py)
    elif screen_py > (visible_rows - dead_zone - 1):
        camera_y += (screen_py - (visible_rows - dead_zone - 1))

    if camera_x < 0:
        camera_x = 0
    if camera_y < 0:
        camera_y = 0
    if camera_x > (world_width - visible_cols):
        camera_x = (world_width - visible_cols)
    if camera_y > (world_height - visible_rows):
        camera_y = (world_height - visible_rows)

    return camera_x, camera_y


def center_camera_on_player(model, stdscr, map_top_offset: int) -> None:
    max_scr_rows, max_scr_cols = stdscr.getmaxyx()
    visible_cols = max_scr_cols
    visible_rows = max_scr_rows - map_top_offset

    model.camera_x = model.player.x - (visible_cols // 2)
    model.camera_y = model.player.y - (visible_rows // 2)

    if model.camera_x < 0:
        model.camera_x = 0
    if model.camera_y < 0:
        model.camera_y = 0
    if model.camera_x > (model.world_width - visible_cols):
        model.camera_x = (model.world_width - visible_cols)
    if model.camera_y > (model.world_height - visible_rows):
        model.camera_y = (model.world_height - visible_rows)


def partial_scroll(model, stdscr, dx: int, dy: int, map_top_offset: int) -> None:
    max_scr_rows, max_scr_cols = stdscr.getmaxyx()
    visible_cols = max_scr_cols
    visible_rows = max_scr_rows - map_top_offset

    def fallback_reblit():
        for row in range(model.camera_y, model.camera_y + visible_rows):
            for col in range(model.camera_x, model.camera_x + visible_cols):
                model.dirty_tiles.add((col, row))

    if abs(dx) > 1 or abs(dy) > 1:
        fallback_reblit()
        return

    stdscr.setscrreg(map_top_offset, max_scr_rows - 1)

    try:
        if dy == 1:
            stdscr.scroll(1)
            new_row = model.camera_y + visible_rows - 1
            for col in range(model.camera_x, model.camera_x + visible_cols):
                model.dirty_tiles.add((col, new_row))
        elif dy == -1:
            stdscr.scroll(-1)
            new_row = model.camera_y
            for col in range(model.camera_x, model.camera_x + visible_cols):
                model.dirty_tiles.add((col, new_row))
        elif dx == 1:
            for screen_row in range(map_top_offset, map_top_offset + visible_rows):
                line_bytes = stdscr.instr(screen_row, 1, visible_cols - 1)
                safe_addstr(stdscr, screen_row, 0,
                            line_bytes.decode("utf-8", "ignore"),
                            0,
                            clip_borders=True)
                safe_addch(stdscr, screen_row, visible_cols - 1, ' ', 0, clip_borders=True)
            new_col = model.camera_x + visible_cols - 1
            for row in range(model.camera_y, model.camera_y + visible_rows):
                model.dirty_tiles.add((new_col, row))
        elif dx == -1:
            for screen_row in range(map_top_offset, map_top_offset + visible_rows):
                line_bytes = stdscr.instr(screen_row, 0, visible_cols - 1)
                safe_addstr(stdscr, screen_row, 1,
                            line_bytes.decode("utf-8", "ignore"),
                            0,
                            clip_borders=True)
                safe_addch(stdscr, screen_row, 0, ' ', 0, clip_borders=True)
            new_col = model.camera_x
            for row in range(model.camera_y, model.camera_y + visible_rows):
                model.dirty_tiles.add((new_col, row))

    except curses.error:
        fallback_reblit()

    stdscr.setscrreg(0, max_scr_rows - 1)