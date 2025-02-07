# FileName: engine_main.py
# version: 4.0 (modernized and modularized game engine loop)
#
# Summary:
#   Core game loop restructured in an object‑oriented, modular style.
#   The GameEngine class encapsulates input processing, camera updates,
#   game logic updates, and rendering in separate methods.
#   The run() method loops until the model signals a quit.
#
# Tags: engine, main, loop, modular

from .engine_camera import update_camera_with_deadzone, center_camera_on_player
from .engine_framerate import manage_framerate
from .controls.controls_main import (
    handle_common_actions,
    handle_editor_actions,
    handle_play_actions,
)
from .engine_respawn import handle_respawns
from engine_actionflash import update_action_flash
from .engine_npc import update_npcs
from .engine_network import handle_network
from scenery.tile_effects import apply_tile_effects
from scenery.scenery_core import get_scenery_def_id_at

class GameEngine:
    def __init__(self, model, context, game_input, game_renderer):
        """
        Initialize the game engine with the provided model, context,
        input handler, and renderer.
        """
        self.model = model
        self.context = context
        self.game_input = game_input
        self.game_renderer = game_renderer

        # Pass the context to the model.
        self.model.context = context

        # Center the camera on the player at startup.
        visible_cols, visible_rows = self.game_renderer.get_visible_size()
        center_camera_on_player(self.model, visible_cols, visible_rows)

        self.model.full_redraw_needed = True
        self.model.should_quit = False
        self.model.ui_scroll_dx = 0
        self.model.ui_scroll_dy = 0

    def mark_dirty(self, x, y):
        """Mark a tile as dirty so it will be re-drawn."""
        self.model.dirty_tiles.add((x, y))

    def process_input(self):
        """
        Poll for input actions and process them.
        This method applies common, editor, and play controls.
        """
        actions = self.game_input.get_actions()
        for act in actions:
            # Process common actions (e.g. movement, quit)
            did_move, want_quit = handle_common_actions(act, self.model, self.game_renderer, self.mark_dirty)
            if want_quit:
                self.model.should_quit = True
                break

            # Process editor-specific actions (if any)
            self.model.full_redraw_needed = handle_editor_actions(
                act, self.model, self.game_renderer, self.model.full_redraw_needed, self.mark_dirty
            )

            # Process play-specific actions (game controls)
            self.model.full_redraw_needed = handle_play_actions(
                act, self.model, self.game_renderer, self.model.full_redraw_needed, self.mark_dirty
            )
        return actions

    def update_camera(self):
        """
        Update the camera position based on the player's position.
        Uses a deadzone, and forces a full redraw if the movement is significant.
        """
        old_cam_x, old_cam_y = self.model.camera_x, self.model.camera_y
        visible_cols, visible_rows = self.game_renderer.get_visible_size()

        # Update camera without clamping to world bounds.
        self.model.camera_x, self.model.camera_y = update_camera_with_deadzone(
            self.model.player.x,
            self.model.player.y,
            self.model.camera_x,
            self.model.camera_y,
            visible_cols,
            visible_rows,
            dead_zone=2
        )
        dx = self.model.camera_x - old_cam_x
        dy = self.model.camera_y - old_cam_y
        self.model.ui_scroll_dx = dx
        self.model.ui_scroll_dy = dy

        # Force a full redraw if the camera has jumped more than one tile.
        if abs(dx) > 1 or abs(dy) > 1:
            self.model.full_redraw_needed = True

    def update_game_logic(self):
        """
        Update various game logic components, including network, NPC behavior,
        respawns, sliding effects, and temporary action flashes.
        """
        handle_network(self.model)
        update_npcs(self.model, self.mark_dirty)
        handle_respawns(self.model, self.mark_dirty)

        # Optional: Apply sliding effects when no input is detected.
        if self.context.enable_sliding and not self.game_input.get_actions():
            tile_def_id = get_scenery_def_id_at(
                self.model.player.x, self.model.player.y, self.model.placed_scenery
            )
            old_px, old_py = self.model.player.x, self.model.player.y
            apply_tile_effects(
                self.model.player,
                tile_def_id,
                self.model.placed_scenery,
                is_editor=self.context.enable_editor_commands
            )
            if (self.model.player.x, self.model.player.y) != (old_px, old_py):
                self.mark_dirty(old_px, old_py)
                self.mark_dirty(self.model.player.x, self.model.player.y)

        update_action_flash(self.model, self.mark_dirty)

    def render(self):
        """
        Render the current game state. After drawing, clear the set of dirty tiles.
        """
        self.game_renderer.render(self.model)
        self.model.dirty_tiles.clear()

    def run(self, target_fps=20):
        """
        Run the main game loop until the model signals to quit.
        This loop processes input, updates the camera and game logic,
        renders the scene, and maintains the target framerate.
        """
        while not self.model.should_quit:
            self.process_input()
            self.update_camera()
            self.update_game_logic()
            self.render()
            manage_framerate(target_fps)

def run_game_loop(model, context, game_input, game_renderer):
    """
    Entry point for running the game loop.
    Initializes a GameEngine instance and starts the loop.
    """
    engine = GameEngine(model, context, game_input, game_renderer)
    engine.run()