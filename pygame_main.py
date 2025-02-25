# File: pygame_main.py
# version: 1.1
#
# Summary: Entry point for the pygame application.
# Initializes pygame, sets up the display, updates dynamic UI scaling,
# and launches the MenuFlowManager.
# Tags: pygame, main, ui

def main():
    # Defer pygame-specific imports until runtime.
    import pygame
    from frontends.pygame.pygame_menu_flow_manager import MenuFlowManager
    from frontends.pygame.pygame_utils import create_display, update_cell_sizes

    pygame.init()
    
    # Create the display using our helper.
    screen = create_display()
    
    # Update UI scaling based on the current screen size.
    update_cell_sizes(screen)
    
    # Instantiate and run the menu flow manager.
    menu_manager = MenuFlowManager(screen)
    menu_manager.run()
    
    pygame.quit()

if __name__ == '__main__':
    main()