# FileName: model_main.py
# Holds a GameModel class that stores all game-related state in one place.

class GameModel:
    def __init__(self):
        # Core references
        self.player = None

        # Instead of a list, store a dictionary for placed_scenery
        # so collisions and rendering see the same data structure.
        # Example: (x, y) -> [SceneryObject, SceneryObject, ...]
        self.placed_scenery = {}

        # World geometry
        self.world_width = 100
        self.world_height = 60

        # Context (play vs. editor settings)
        self.context = None

        # Respawn logic (for trees, rocks, etc.)
        self.respawn_list = []

        # Editor-related fields
        self.editor_scenery_list = []
        self.editor_scenery_index = 0

        # [ADDED for Undo] Track recently placed objects for undo
        self.editor_undo_stack = []

        # Camera and rendering
        self.camera_x = 0
        self.camera_y = 0
        self.dirty_tiles = set()
        self.action_flash_info = None
        self.full_redraw_needed = True