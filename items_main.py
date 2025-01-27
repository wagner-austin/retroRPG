# File: items_main.py
# version: 1.0
"""
Holds global item definitions and the ItemInstance class.

Usage:
    from items import ALL_ITEMS, ItemInstance
"""

##############################################################################
# 1) Item Registry
##############################################################################

ALL_ITEMS = {
    "BasicSword": {
        "slot": "weapon",
        "bonus_stats": {"attack": 2}
    },
    "HealingPotion": {
        "consumable": True,
        "use_func": "heal_20hp"
    },
    "IronArmor": {
        "slot": "armor",
        "bonus_stats": {"defense": 3}
    },
    # Add more items as needed
}

##############################################################################
# 2) ItemInstance class
##############################################################################

class ItemInstance:
    """
    Represents one "instance" of an item in a player's inventory.
    - definition_id => key in ALL_ITEMS
    - instance_data => dict for overrides (e.g. custom name, color, etc.)

    Example usage:
        sword = ItemInstance("BasicSword", {"custom_name": "Sword of Fire", "attack_bonus": 5})
    """
    def __init__(self, definition_id, instance_data=None):
        self.definition_id = definition_id
        if instance_data is None:
            instance_data = {}
        self.instance_data = instance_data  # Could store durability, enchantments, etc.

    @property
    def base_def(self):
        """
        Returns the base item definition from ALL_ITEMS.
        e.g. base_def["slot"], base_def["consumable"], etc.
        """
        return ALL_ITEMS.get(self.definition_id, {})

    def get_slot(self):
        """
        Returns the equip slot if any. e.g. "weapon", "armor", or None
        """
        return self.base_def.get("slot")

    def is_consumable(self):
        """
        Returns True if item is consumable, else False
        """
        return self.base_def.get("consumable", False)

    def get_bonus_stats(self):
        """
        Combine base_def's bonus_stats with any instance overrides.
        e.g. base bonus_stats => {"attack":2}, instance_data => {"attack_bonus":5}
        """
        base = self.base_def.get("bonus_stats", {})
        # Merge with instance_data keys if relevant
        # For example, instance_data might store extra bonus points
        combined = dict(base)  # shallow copy
        # If we have "attack_bonus" in instance_data, add it to combined
        if "attack_bonus" in self.instance_data:
            combined["attack"] = combined.get("attack", 0) + self.instance_data["attack_bonus"]
        return combined

    def __repr__(self):
        return f"<ItemInstance({self.definition_id}, data={self.instance_data})>"
