# FileName: engine_camera.py
# version: 2.8 (modified for infinite map)
# Summary: Implements camera logic with no bounding.
# Tags: engine, camera, scrolling

from typing import Tuple

def update_camera_with_deadzone(player_x: int, player_y: int,
                                camera_x: int, camera_y: int,
                                visible_cols: int, visible_rows: int,
                                dead_zone: int = 3) -> Tuple[int, int]:
    """
    Adjust camera_x, camera_y so the player remains within the 'dead_zone' inside
    the visible window. No bounding to any min/max.
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

    # Removed all clamping to a 'world_width'/'world_height'.
    return camera_x, camera_y

def center_camera_on_player(model, visible_cols: int, visible_rows: int) -> None:
    """
    Centers the camera on the player's position with no bounding.
    """
    px = model.player.x
    py = model.player.y

    model.camera_x = px - (visible_cols // 2)
    model.camera_y = py - (visible_rows // 2)
    # No clamp