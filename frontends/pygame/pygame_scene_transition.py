# File: pygame_scene_transition.py
# version: 1.2
#
# Summary:
#   Provides a CrossFadeTransitionScene that smoothly blends from one scene to another
#   using an overlaid rain effect. Also contains a helper function (run_transition)
#   that runs the transition based on a centralized configuration (TRANSITION_CONFIG).
#
# Tags: transition, scene, effects, helper

import pygame
import random
from .pygame_scene_base import Scene
from .pygame_scene_layer_base import SceneLayer
from .pygame_common import draw_inside_frame_ch
from .pygame_color_init import get_foreground

# Global configuration for transitions.
TRANSITION_CONFIG = {
    "enabled": True,             # Set to False to disable transitions.
    "effect": "crossfade",       # Currently, only "crossfade" is implemented.
    "phase1_duration": 150,      # Duration (in dt units) for Phase 1 (rain increases over current scene).
    "phase2_duration": 150,      # Duration for Phase 2 (rain fades over next scene).
    "dt_increment": 10,          # Time increment (dt) per frame.
    "napms": 10,                 # Delay (in ms) between frames.
    "color": "blue_on_black",    # Color for the rain effect.
}


class CrossFadeBackgroundLayer(SceneLayer):
    """
    Renders the background for the transition.
    For dt < phase1_duration, it draws the entire current scene;
    for dt ≥ phase1_duration, it draws the entire next scene.
    """
    def __init__(self, current_scene, next_scene, phase1_duration, phase2_duration):
        super().__init__(name="crossfade_background", z_index=100)
        self.current_scene = current_scene
        self.next_scene = next_scene
        self.phase1_duration = phase1_duration
        self.phase2_duration = phase2_duration

    def draw(self, renderer, dt, context):
        # In Phase 1, draw the current scene; after that, draw the next scene.
        if dt < self.phase1_duration:
            for layer in self.current_scene.layers:
                layer.draw(renderer, dt, context)
        else:
            for layer in self.next_scene.layers:
                layer.draw(renderer, dt, context)


class CrossFadeRainLayer(SceneLayer):
    """
    Overlays a rain effect whose density varies with dt.
    In Phase 1, density increases linearly from 0 to max_drops;
    in Phase 2, density decreases linearly from max_drops to 0.
    """
    def __init__(self, max_drops=100, color_name="blue_on_black", phase1_duration=500, phase2_duration=500):
        super().__init__(name="crossfade_rain", z_index=600)
        self.max_drops = max_drops
        self.color_name = color_name
        self.phase1_duration = phase1_duration
        self.phase2_duration = phase2_duration

    def _generate_raindrops(self, screen, num_drops):
        # Assume screen.get_size() returns (width, height) in grid units.
        width, height = screen.get_size()
        drops = []
        for _ in range(num_drops):
            # Ensure drops appear inside the frame (avoid borders).
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 2)
            drops.append({"x": x, "y": y})
        return drops

    def draw(self, renderer, dt, context):
        screen = renderer.screen
        if dt < self.phase1_duration:
            density_factor = dt / self.phase1_duration
        else:
            phase2_dt = dt - self.phase1_duration
            density_factor = max(0, 1 - (phase2_dt / self.phase2_duration))
        num_drops = int(self.max_drops * density_factor)
        drops = self._generate_raindrops(screen, num_drops)
        attr = get_foreground(self.color_name)
        for drop in drops:
            # Draw a rain drop (here represented by a vertical bar).
            try:
                ch = '|'
                draw_inside_frame_ch(screen, drop["y"], drop["x"], ch, attr)
            except Exception:
                # In pygame, drawing errors are less common.
                pass


class CrossFadeTransitionScene(Scene):
    """
    A scene that performs a cross-fade transition between two scenes using a rain overlay.
    The transition is complete when dt >= (phase1_duration + phase2_duration).
    """
    def __init__(self, current_scene, next_scene, phase_duration=(500, 500)):
        super().__init__()
        self.current_scene = current_scene
        self.next_scene = next_scene
        self.phase1_duration, self.phase2_duration = phase_duration
        self.frame_count = 0  # Updated externally via run_transition.
        self.background_layer = CrossFadeBackgroundLayer(current_scene, next_scene,
                                                           self.phase1_duration, self.phase2_duration)
        self.rain_layer = CrossFadeRainLayer(max_drops=100,
                                             color_name=TRANSITION_CONFIG["color"],
                                             phase1_duration=self.phase1_duration,
                                             phase2_duration=self.phase2_duration)
        self.layers = [self.background_layer, self.rain_layer]

    def handle_input(self, key):
        # Ignore user input during transition.
        return None

    def is_complete(self):
        total_duration = self.phase1_duration + self.phase2_duration
        return self.frame_count >= total_duration


def run_transition(screen, current_scene, next_scene):
    """
    Runs a transition from current_scene to next_scene based on the global TRANSITION_CONFIG.
    This helper handles all timing, color, effect type, and enabling/disabling.
    Modify TRANSITION_CONFIG here to change the transition globally.
    """
    if not TRANSITION_CONFIG.get("enabled", True):
        return
    phase1 = TRANSITION_CONFIG.get("phase1_duration", 500)
    phase2 = TRANSITION_CONFIG.get("phase2_duration", 500)
    dt_increment = TRANSITION_CONFIG.get("dt_increment", 10)
    napms_delay = TRANSITION_CONFIG.get("napms", 10)
    # Currently, only "crossfade" is implemented.
    from .pygame_game_renderer import PygameGameRenderer
    transition_scene = CrossFadeTransitionScene(current_scene, next_scene,
                                                  phase_duration=(phase1, phase2))
    # Update rain color from configuration.
    transition_scene.rain_layer.color_name = TRANSITION_CONFIG.get("color", "blue_on_black")
    renderer = PygameGameRenderer(screen)
    dt = 0
    while not transition_scene.is_complete():
        renderer.render_scene(transition_scene, dt=dt, context=None)
        dt += dt_increment
        pygame.time.delay(napms_delay)
        transition_scene.frame_count = dt