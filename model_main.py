# FileName: model_main.py
# version: 1.3 (now includes editor_scenery_list, editor_scenery_index)
# Summary: Defines the GameModel class and the GameContext class.
# Tags: model, data, state

class GameModel:
    def __init__(self):
        """
        Stores the main world and player state:
          - player
          - placed_scenery (dict-of-layers)
          - world_width, world_height
          - camera_x, camera_y
          - dirty_tiles, action_flash_info
          - loaded_map_filename
          - full_redraw_needed, should_quit
          - respawn_list
          - editor_scenery_list, editor_scenery_index (used by controls_main, etc.)
        """
        self.player = None
        self.placed_scenery = {}
        self.world_width = 100
        self.world_height = 60

        # Camera & partial updates
        self.camera_x = 0
        self.camera_y = 0
        self.dirty_tiles = set()
        self.action_flash_info = None

        # If you want to track the loaded map filename
        self.loaded_map_filename = None

        # A flag for the main loop to do a full redraw if needed
        self.full_redraw_needed = True

        # A flag for the main loop to quit
        self.should_quit = False

        # For respawning resources
        self.respawn_list = []

        # For editor mode
        self.editor_scenery_list = []
        self.editor_scenery_index = 0
        self.editor_undo_stack = []


class GameContext:
    """
    Holds high-level mode flags (play vs. editor) and feature toggles (respawn, etc.).
    Moved here so that 'play_runner.py' can import it from model_main.
    """
    def __init__(self, mode_name="play"):
        self.mode_name = mode_name
        self.enable_editor_commands = False
        self.enable_sliding = False
        self.enable_respawn = False
        self.require_bridge_supplies = False
        self.enable_monster_ai = False
        self.enable_damage = False

        if mode_name == "editor":
            self.enable_editor_commands = True
            self.enable_sliding = False
            self.enable_respawn = False
            self.enable_monster_ai = False
            self.enable_damage = False
        elif mode_name == "play":
            self.enable_editor_commands = False
            self.enable_sliding = True
            self.enable_respawn = True