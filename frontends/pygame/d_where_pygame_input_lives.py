# FileName: where_pygame_input_lives.py
# version: 2.4
#
# Summary: A pygame-based front-end implementing IGameInput for user interaction.
#          Processes pygame events to return a list of action strings like
#          ["MOVE_UP", "QUIT", "INTERACT", etc.]. Note that only 'q'/ESC quits,
#          and 'i' or 'I' maps to SHOW_INVENTORY.
#
# Tags: pygame, ui, rendering

import pygame
from engine.engine_interfaces import IGameInput

class PygameGameInput(IGameInput):
    """
    Implements IGameInput for pygame. The get_actions() method processes pygame events,
    returning a list of action strings like ["MOVE_UP", "QUIT", "INTERACT", etc.].
    """

    def __init__(self):
        # Optionally, enable key repeat (parameters can be adjusted as needed)
        pygame.key.set_repeat(1, 10)
        # Hide the mouse cursor for a cleaner UI
        pygame.mouse.set_visible(False)

    def get_actions(self):
        actions = []
        # Process events from the pygame event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions.append("QUIT")
            elif event.type == pygame.KEYDOWN:
                act = self._interpret_key(event.key)
                if act:
                    actions.append(act)
        return actions

    def _interpret_key(self, key):
        # Quit => q, or ESC
        if key in (pygame.K_q, pygame.K_ESCAPE):
            return "QUIT"

        # Movement
        if key in (pygame.K_w, pygame.K_UP):
            return "MOVE_UP"
        if key in (pygame.K_s, pygame.K_DOWN):
            return "MOVE_DOWN"
        if key in (pygame.K_a, pygame.K_LEFT):
            return "MOVE_LEFT"
        if key in (pygame.K_d, pygame.K_RIGHT):
            return "MOVE_RIGHT"

        # Editor toggle
        if key == pygame.K_e:
            return "EDITOR_TOGGLE"

        # Quick-save
        if key == pygame.K_o:
            return "SAVE_QUICK"

        # Debug
        if key == pygame.K_v:
            return "DEBUG_TOGGLE"

        # Interact (space bar)
        if key == pygame.K_SPACE:
            return "INTERACT"

        # Editor keys
        if key == pygame.K_p:
            return "PLACE_ITEM"
        if key == pygame.K_x:
            return "REMOVE_TOP"
        if key == pygame.K_u:
            return "UNDO"
        if key == pygame.K_l:
            return "NEXT_ITEM"
        if key == pygame.K_k:
            return "PREV_ITEM"

        # Show Inventory
        if key == pygame.K_i:
            return "SHOW_INVENTORY"

        return None
