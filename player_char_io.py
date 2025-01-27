# FileName: player_char_io.py
# version: 2.1 (UNIFIED SINGLE-SAVE FILE, stored in "character/character_data.json")
"""
Handles saving/loading the Player object to JSON (single file),
stored in a "character" subfolder.

No partial merges. We overwrite the JSON with the current data
whenever we save.
"""

import os
import json

from items_main import ItemInstance
from player_char import Player

CHARACTER_FOLDER = "character"
CHARACTER_FILE = os.path.join(CHARACTER_FOLDER, "character_data.json")

def save_player(player, filename=CHARACTER_FILE):
    """
    Write player's data to 'filename' as JSON.

    This includes:
      - name, hp, level
      - x, y (map position)
      - gold, wood, stone
      - entire inventory (list of items)
      - equipped items
    """
    # Ensure the "character" folder exists
    os.makedirs(CHARACTER_FOLDER, exist_ok=True)

    data = {
        "name": player.name,
        "hp": player.hp,
        "level": player.level,
        "x": player.x,
        "y": player.y,
        "gold": player.gold,
        "wood": player.wood,
        "stone": player.stone,
        "inventory": [],
        "equipped": {},
    }

    # Fill inventory
    for item in player.inventory:
        data["inventory"].append({
            "definition_id": item.definition_id,
            "instance_data": item.instance_data
        })

    # Fill equipped
    for slot, item in player.equipped.items():
        if item:
            data["equipped"][slot] = {
                "definition_id": item.definition_id,
                "instance_data": item.instance_data
            }
        else:
            data["equipped"][slot] = None

    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving player: {e}")


def load_player(filename=CHARACTER_FILE):
    """
    Read JSON from 'filename' => build a Player object => return it.
    If file not found or error, return None.

    Reconstructs each item as ItemInstance(definition_id, instance_data).
    """
    if not os.path.exists(filename):
        return None

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except:
        return None

    # Build player
    name = data.get("name", "Hero")
    hp = data.get("hp", 100)
    level = data.get("level", 1)

    player = Player(
        x=data.get("x", 0),
        y=data.get("y", 0),
        name=name,
        hp=hp,
        level=level
    )
    player.gold = data.get("gold", 0)
    player.wood = data.get("wood", 0)
    player.stone = data.get("stone", 0)

    # Rebuild inventory
    inv_list = data.get("inventory", [])
    for it in inv_list:
        definition_id = it.get("definition_id", "")
        instance_data = it.get("instance_data", {})
        item_instance = ItemInstance(definition_id, instance_data)
        player.add_item(item_instance)

    # Rebuild equipped
    eq_dict = data.get("equipped", {})
    for slot, info in eq_dict.items():
        if info:
            definition_id = info.get("definition_id", "")
            instance_data = info.get("instance_data", {})
            eq_item = ItemInstance(definition_id, instance_data)
            player.equipped[slot] = eq_item
        else:
            player.equipped[slot] = None

    return player