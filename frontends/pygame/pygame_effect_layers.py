# File: pygame_effect_layers.py
# version: 1.3
#
# Summary:
#   Provides plugin layer classes for dynamic weather effects: Snow and Rain.
#   These layers now use unified drawing helpers and reinitialize when the screen size changes.
#
# Tags: effects, snow, rain, scene, plugin

import random
from .pygame_scene_layer_base import SceneLayer
from .pygame_color_init import get_foreground
from .pygame_common import draw_inside_frame_ch

class SnowEffectLayer(SceneLayer):
    def __init__(self, num_flakes=50, color_name="white_on_black"):
        # Use a high z_index so the snow appears on top.
        super().__init__("snow_effect", 300)
        self.num_flakes = num_flakes
        self.color_name = color_name
        self.snowflakes = []
        self.initialized = False
        self.last_width = None
        self.last_height = None

    def _initialize_snowflakes(self, width, height):
        self.snowflakes = []
        for _ in range(self.num_flakes):
            # Ensure the snowflake is drawn inside the frame.
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 2)
            self.snowflakes.append({"x": x, "y": y})
        self.last_width = width
        self.last_height = height
        self.initialized = True

    def draw(self, renderer, dt, context):
        screen = renderer.screen
        width, height = screen.get_size()
        # Reinitialize if the screen size has changed.
        if not self.initialized or width != self.last_width or height != self.last_height:
            self._initialize_snowflakes(width, height)
        # Update snowflake positions every 100 frames.
        if dt % 100 == 0:
            for flake in self.snowflakes:
                flake["y"] += 1
                if flake["y"] >= height - 1:
                    flake["y"] = 1
                    flake["x"] = random.randint(1, width - 2)
        attr = get_foreground(self.color_name)
        for flake in self.snowflakes:
            ch = random.choice(['*', '.'])
            draw_inside_frame_ch(screen, flake["y"], flake["x"], ch, attr)

class RainEffectLayer(SceneLayer):
    def __init__(self, num_drops=50, color_name="blue_on_black", direction="down"):
        # Use a high z_index so the rain appears above other layers.
        super().__init__("rain_effect", 300)
        self.num_drops = num_drops
        self.color_name = color_name
        self.direction = direction.lower()  # Accept "down", "left", or "right"
        self.raindrops = []
        self.initialized = False
        self.last_width = None
        self.last_height = None

    def _initialize_raindrops(self, width, height):
        self.raindrops = []
        for _ in range(self.num_drops):
            # Ensure the raindrop is drawn inside the frame.
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 2)
            self.raindrops.append({"x": x, "y": y})
        self.last_width = width
        self.last_height = height
        self.initialized = True

    def draw(self, renderer, dt, context):
        screen = renderer.screen
        width, height = screen.get_size()
        # Reinitialize if needed.
        if not self.initialized or width != self.last_width or height != self.last_height:
            self._initialize_raindrops(width, height)
        # Update raindrop positions every 100 frames.
        if dt % 100 == 0:
            for drop in self.raindrops:
                if self.direction == "down":
                    drop["y"] += 1
                    if drop["y"] >= height - 1:
                        drop["y"] = 1
                        drop["x"] = random.randint(1, width - 2)
                elif self.direction == "left":
                    drop["x"] -= 1
                    if drop["x"] < 1:
                        drop["x"] = width - 2
                        drop["y"] = random.randint(1, height - 2)
                elif self.direction == "right":
                    drop["x"] += 1
                    if drop["x"] >= width - 1:
                        drop["x"] = 1
                        drop["y"] = random.randint(1, height - 2)
        attr = get_foreground(self.color_name)
        for drop in self.raindrops:
            ch = '|' if self.direction == "down" else '-'
            draw_inside_frame_ch(screen, drop["y"], drop["x"], ch, attr)