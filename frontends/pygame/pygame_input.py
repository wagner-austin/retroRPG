# FileName: pygame_input.py
# version: 1.0
# Summary: Pygame-based input class implementing IGameInput from engine_interfaces.
# Tags: input, pygame

import pygame
from engine.engine_interfaces import IGameInput

class PygameGameInput(IGameInput):
    """
    Gathers user events from pygame.event.get(), 
    returns a list of high-level action strings ("MOVE_UP", "QUIT", etc.).
    """

    def get_actions(self):
        actions = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions.append("QUIT")

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    actions.append("QUIT")

                elif event.key in (pygame.K_w, pygame.K_UP):
                    actions.append("MOVE_UP")
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    actions.append("MOVE_DOWN")
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    actions.append("MOVE_LEFT")
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    actions.append("MOVE_RIGHT")

                elif event.key == pygame.K_SPACE:
                    actions.append("INTERACT")
                elif event.key == pygame.K_e:
                    actions.append("EDITOR_TOGGLE")
                elif event.key == pygame.K_o:
                    actions.append("SAVE_QUICK")
                elif event.key == pygame.K_v:
                    actions.append("DEBUG_TOGGLE")

                # Editor
                elif event.key in (pygame.K_p, ):
                    actions.append("PLACE_ITEM")
                elif event.key in (pygame.K_x, ):
                    actions.append("REMOVE_TOP")
                elif event.key in (pygame.K_u, ):
                    actions.append("UNDO")
                elif event.key in (pygame.K_l, ):
                    actions.append("NEXT_ITEM")
                elif event.key in (pygame.K_k, ):
                    actions.append("PREV_ITEM")

                # Show Inventory
                elif event.key in (pygame.K_i, ):
                    actions.append("SHOW_INVENTORY")

        return actions
