# FileName: player_char.py
# version: 1.2
# Summary: Defines the Player class with movement, stats, and inventory fields used in the game engine.
# Tags: player, character, movement

import debug
from scenery_main import is_blocked

class Player:
    def __init__(
        self,
        x=0,
        y=0,
        name="Hero",
        hp=100,
        level=1,
        char="@"
    ):
        """
        A unified Player constructor that supports position, name, hp, level,
        plus a 'char' attribute for rendering.

        If you'd like to load 'char' from JSON, simply add it to your load/save logic.
        """
        self.x = x
        self.y = y
        self.name = name
        self.hp = hp
        self.level = level

        # The character used when drawing the player on-screen
        self.char = char

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

        # Clamp to world boundaries
        new_x = max(0, min(new_x, world_width - 1))
        new_y = max(0, min(new_y, world_height - 1))

        # If debug mode is ON and ignore_collisions is True, skip collision checks
        if debug.DEBUG_CONFIG["enabled"] and debug.DEBUG_CONFIG["ignore_collisions"]:
            self.x = new_x
            self.y = new_y
        else:
            # Normal collision check
            if not is_blocked(new_x, new_y, placed_scenery):
                self.x = new_x
                self.y = new_y