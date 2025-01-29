# FileName: engine_camera.py
# version: 2.4 (unified partial_scroll logic)
# Summary: Implements camera logic (dead-zone scrolling, centering) to keep the player in view on large maps.
#          partial_scroll now handles both horizontal/vertical shifts in one function.
# Tags: engine, camera, scrolling

import curses

def update_camera_with_deadzone(player_x, player_y,
                                camera_x, camera_y,
                                visible_cols, visible_rows,
                                world_width, world_height,
                                dead_zone=2):
    """
    Moves the camera only if the player is within 'dead_zone' tiles of an edge.
    Prevents constant recentering on small moves.
    Returns (new_camera_x, new_camera_y).
    """
    screen_px = player_x - camera_x
    screen_py = player_y - camera_y

    # Horizontal deadzone
    if screen_px < dead_zone:
        camera_x -= (dead_zone - screen_px)
    elif screen_px > (visible_cols - dead_zone - 1):
        camera_x += (screen_px - (visible_cols - dead_zone - 1))

    # Vertical deadzone
    if screen_py < dead_zone:
        camera_y -= (dead_zone - screen_py)
    elif screen_py > (visible_rows - dead_zone - 1):
        camera_y += (screen_py - (visible_rows - dead_zone - 1))

    # Clamp
    if camera_x < 0:
        camera_x = 0
    if camera_y < 0:
        camera_y = 0
    if camera_x > (world_width - visible_cols):
        camera_x = (world_width - visible_cols)
    if camera_y > (world_height - visible_rows):
        camera_y = (world_height - visible_rows)

    return camera_x, camera_y

def center_camera_on_player(model, stdscr, map_top_offset):
    """
    Centers the camera on the player initially (or whenever called).
    """
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

def partial_scroll(model, stdscr, dx, dy, map_top_offset):
    """
    Scrolls the screen by 1 tile horizontally or vertically if dx=±1 or dy=±1.
    If dx or dy is larger than ±1 (meaning a big jump), we rely on a full redraw.

    We unify the old partial_scroll_vertical and partial_scroll_horizontal.
    """
    max_scr_rows, max_scr_cols = stdscr.getmaxyx()
    visible_cols = max_scr_cols
    visible_rows = max_scr_rows - map_top_offset

    def fallback_reblit():
        for row in range(model.camera_y, model.camera_y + visible_rows):
            for col in range(model.camera_x, model.camera_x + visible_cols):
                model.dirty_tiles.add((col, row))

    # If the camera jumped more than 1 tile, fallback
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
            # Move everything left by 1 column
            for screen_row in range(map_top_offset, map_top_offset + visible_rows):
                line_bytes = stdscr.instr(screen_row, 1, visible_cols - 1)
                stdscr.addstr(screen_row, 0, line_bytes)
                stdscr.addch(screen_row, visible_cols - 1, ' ')
            new_col = model.camera_x + visible_cols - 1
            for row in range(model.camera_y, model.camera_y + visible_rows):
                model.dirty_tiles.add((new_col, row))
        elif dx == -1:
            # Move everything right by 1 column
            for screen_row in range(map_top_offset, map_top_offset + visible_rows):
                line_bytes = stdscr.instr(screen_row, 0, visible_cols - 1)
                stdscr.addstr(screen_row, 1, line_bytes)
                stdscr.addch(screen_row, 0, ' ')
            new_col = model.camera_x
            for row in range(model.camera_y, model.camera_y + visible_rows):
                model.dirty_tiles.add((new_col, row))

    except curses.error:
        fallback_reblit()

    stdscr.setscrreg(0, max_scr_rows - 1)