# FileName: entities_main.py
# version: 1.0
# Summary: Defines entity logic or classes for monsters, NPCs, or interactive objects in the game world.
# Tags: entities, ai, monster, npc

class Monster:
    def __init__(self, x, y, name="Goblin"):
        self.x = x
        self.y = y
        self.name = name
        self.hp = 10
        self.attack = 2
        self.defense = 1

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            # monster dies
            pass

class Item:
    def __init__(self, x, y, item_type="potion"):
        self.x = x
        self.y = y
        self.item_type = item_type

    def on_pickup(self, player):
        pass