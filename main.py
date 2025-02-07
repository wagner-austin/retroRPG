## FileName: RetroRPG.py
# version: 1.6
# Summary: Main entry point for RetroRPG, handling high-level init, then calling MenuFlowManager.
# Tags: main, entry, initialization

import time

def main():
    # Defer curses import to inside the main() function, so we avoid it at top-level.
    import curses
    # Updated import to reference the new location for MenuFlowManager
    from curses_frontend.curses_menu_flow_manager import MenuFlowManager

    def run_game(stdscr):
        # Let terminal size stabilize briefly (was curses.napms(100) before)
        time.sleep(0.1)

        # Create and run the menu flow manager
        flow_manager = MenuFlowManager(stdscr)
        flow_manager.run()

    curses.wrapper(run_game)

if __name__ == "__main__":
    main()