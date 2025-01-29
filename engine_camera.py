# FileName: engine_camera.py
# version: 2.8 (added center_camera_on_player)
# Summary: Implements camera logic with partial scrolling *logic only* (no curses).
# Tags: engine, camera, scrolling

from typing import Tuple

def update_camera_with_deadzone(player_x: int, player_y: int,
                                camera_x: int, camera_y: int,
                                visible_cols: int, visible_rows: int,
                                world_width: int, world_height: int,
                                dead_zone: int = 2) -> Tuple[int, int]:
    """
    Adjust camera_x, camera_y so the player remains within the 'dead_zone' inside
    the visible window. No direct curses calls: purely numeric logic.
    """
    screen_px = player_x - camera_x
    screen_py = player_y - camera_y

    # Horizontal dead-zone
    if screen_px < dead_zone:
        camera_x -= (dead_zone - screen_px)
    elif screen_px > (visible_cols - dead_zone - 1):
        camera_x += (screen_px - (visible_cols - dead_zone - 1))

    # Vertical dead-zone
    if screen_py < dead_zone:
        camera_y -= (dead_zone - screen_py)
    elif screen_py > (visible_rows - dead_zone - 1):
        camera_y += (screen_py - (visible_rows - dead_zone - 1))

    # Clamp to world boundaries
    if camera_x < 0:
        camera_x = 0
    if camera_y < 0:
        camera_y = 0
    if camera_x > (world_width - visible_cols):
        camera_x = (world_width - visible_cols)
    if camera_y > (world_height - visible_rows):
        camera_y = (world_height - visible_rows)

    return camera_x, camera_y


def center_camera_on_player(model,
                            visible_cols: int,
                            visible_rows: int) -> None:
    """
    Places the camera so that the player is centered in the visible area, 
    then clamps to the map boundaries. This is typically called once 
    at the beginning, so the camera starts out centered on the player.
    """
    px = model.player.x
    py = model.player.y

    # Center the camera so that px, py is in the middle
    model.camera_x = px - (visible_cols // 2)
    model.camera_y = py - (visible_rows // 2)

    # Clamp to world boundaries
    if model.camera_x < 0:
        model.camera_x = 0
    if model.camera_y < 0:
        model.camera_y = 0
    if model.camera_x > (model.world_width - visible_cols):
        model.camera_x = (model.world_width - visible_cols)
    if model.camera_y > (model.world_height - visible_rows):
        model.camera_y = (model.world_height - visible_rows)