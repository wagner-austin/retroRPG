# FileName: model_main.py
# version: 1.3 (modified for infinite map)
# Summary: Defines the GameModel and GameContext. The world_width/world_height
#          remain but are no longer used for bounding in movement or camera.
# Tags: model, data, state

class GameModel:
    def __init__(self):
        """
        Stores the main world and player state:
          - player
          - placed_scenery (dict-of-layers)
          - world_width, world_height (NO LONGER used for bounding)
          - camera_x, camera_y
          - dirty_tiles, action_flash_info
          - etc.
        """
        self.player = None
        self.placed_scenery = {}

        # These remain for generation or saving, but no bounding:
        #self.world_width = 100
        #self.world_height = 60

        self.camera_x = 0
        self.camera_y = 0
        self.dirty_tiles = set()
        self.action_flash_info = None

        self.loaded_map_filename = None
        self.full_redraw_needed = True
        self.should_quit = False

        # For respawning resources
        self.respawn_list = []

        # For editor mode
        self.editor_scenery_list = []
        self.editor_scenery_index = 0
        self.editor_undo_stack = []

class GameContext:
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