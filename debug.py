# FileName: debug.py
# Purpose: Unified debug configuration with multiple features.

DEBUG_CONFIG = {
    "enabled":              False,
    "ignore_collisions":    False,
    "walk_speed_multiplier": 1,
    # You can add more debug features here in the future.
}


def toggle_debug():
    """
    Toggle the global debug configuration on/off. 
    When 'enabled' is True, we set all desired debug features. 
    When 'enabled' is False, we revert them to normal.
    """
    DEBUG_CONFIG["enabled"] = not DEBUG_CONFIG["enabled"]
    if DEBUG_CONFIG["enabled"]:
        # Enable debug features
        DEBUG_CONFIG["ignore_collisions"] = True
        DEBUG_CONFIG["walk_speed_multiplier"] = 4  # Walk 2x faster
    else:
        # Disable debug features
        DEBUG_CONFIG["ignore_collisions"] = False
        DEBUG_CONFIG["walk_speed_multiplier"] = 1