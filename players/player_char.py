# FileName: player_char.py
# version: 1.2 (modified for infinite map)
# Summary: Defines the Player class with movement, stats, and inventory fields used in the game engine.
# Tags: player, character, movement

import debug
from scenery.scenery_core import is_blocked

class Player:
    def __init__(
        self,
        x=0,
        y=0,
        name="Hero",
        hp=100,
        level=1,
        char="@",
        color_name="white_on_black"
    ):
        """
        A unified Player constructor that supports position, name, hp, level,
        plus a 'char' attribute for rendering, and a color_name for the player's
        foreground color.
        """
        self.x = x
        self.y = y
        self.name = name
        self.hp = hp
        self.level = level

        # The character used when drawing the player on-screen
        self.char = char

        # The foreground color used when drawing the player (floor background is handled elsewhere)
        self.color_name = color_name

        # Common resource stats
        self.gold = 0
        self.wood = 0
        self.stone = 0

        # Inventory system (list), and equipment slots (dict)
        self.inventory = []
        self.equipped = {}

        # Last movement direction
        self.last_move_direction = None

    def add_item(self, item_instance):
        """
        Add an item_instance (from items_main.ItemInstance) to the player's inventory.
        """
        self.inventory.append(item_instance)

    def move(self, direction, world_width, world_height, placed_scenery):
        """
        Move the player by 1 tile in the given direction (up/down/left/right).
        If debug mode is ON & ignore_collisions is True, skip collision checks.
        Otherwise, do normal collision blocking.

        NOTE: No more clamping to world boundaries for infinite map.
        """
        dx, dy = 0, 0
        if direction == "up":
            dy = -1
            self.last_move_direction = "up"
        elif direction == "down":
            dy = 1
            self.last_move_direction = "down"
        elif direction == "left":
            dx = -1
            self.last_move_direction = "left"
        elif direction == "right":
            dx = 1
            self.last_move_direction = "right"

        new_x = self.x + dx
        new_y = self.y + dy

        # If debug mode is ON and ignore_collisions is True, skip collision checks
        if debug.DEBUG_CONFIG["enabled"] and debug.DEBUG_CONFIG["ignore_collisions"]:
            self.x = new_x
            self.y = new_y
        else:
            # Normal collision check
            if not is_blocked(new_x, new_y, placed_scenery):
                self.x = new_x
                self.y = new_y