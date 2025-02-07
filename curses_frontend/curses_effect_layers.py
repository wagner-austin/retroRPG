# File: curses_effect_layers.py
# version: 1.2
#
# Summary:
#   Provides plugin layer classes for dynamic weather effects: Snow and Rain.
#   These layers now use drawing helpers to prevent drawing outside of the frame.
#
# Tags: effects, snow, rain, scene, plugin

import curses
import random
from .scene_layer_base import SceneLayer
from .curses_utils import get_color_attr
from .curses_common import draw_inside_frame_ch  # New helper to enforce in-frame drawing

class SnowEffectLayer(SceneLayer):
    def __init__(self, num_flakes=50, color_name="white_on_black"):
        # Set a high z_index so the snow appears on top of all other layers.
        super().__init__(name="snow_effect", z_index=300)
        self.num_flakes = num_flakes
        self.color_name = color_name
        self.snowflakes = []
        self.initialized = False
        self.last_w = None
        self.last_h = None

    def _initialize_snowflakes(self, max_w, max_h):
        self.snowflakes = []
        for _ in range(self.num_flakes):
            # Ensure the snowflake is drawn inside the frame.
            x = random.randint(1, max_w - 2)
            y = random.randint(1, max_h - 2)
            self.snowflakes.append({"x": x, "y": y})
        self.last_w = max_w
        self.last_h = max_h
        self.initialized = True

    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        max_h, max_w = stdscr.getmaxyx()
        # Reinitialize if the screen size has changed or if not yet initialized.
        if (not self.initialized) or (max_w != self.last_w or max_h != self.last_h):
            self._initialize_snowflakes(max_w, max_h)
        # Update snowflake positions every 100 frames.
        if dt % 100 == 0:
            for flake in self.snowflakes:
                flake["y"] += 1
                if flake["y"] >= max_h - 1:
                    flake["y"] = 1
                    flake["x"] = random.randint(1, max_w - 2)
        attr = get_color_attr(self.color_name)
        for flake in self.snowflakes:
            ch = random.choice(['*', '.'])
            draw_inside_frame_ch(stdscr, flake["y"], flake["x"], ch, attr)

class RainEffectLayer(SceneLayer):
    def __init__(self, num_drops=50, color_name="blue_on_black", direction="down"):
        # Use a high z_index so rain appears above other layers.
        super().__init__(name="rain_effect", z_index=300)
        self.num_drops = num_drops
        self.color_name = color_name
        self.direction = direction.lower()  # Accept "down", "left", or "right"
        self.raindrops = []
        self.initialized = False
        self.last_w = None
        self.last_h = None

    def _initialize_raindrops(self, max_w, max_h):
        self.raindrops = []
        for _ in range(self.num_drops):
            # Ensure the raindrop is drawn inside the frame.
            x = random.randint(1, max_w - 2)
            y = random.randint(1, max_h - 2)
            self.raindrops.append({"x": x, "y": y})
        self.last_w = max_w
        self.last_h = max_h
        self.initialized = True

    def draw(self, renderer, dt, context):
        stdscr = renderer.stdscr
        max_h, max_w = stdscr.getmaxyx()
        # Reinitialize if needed.
        if (not self.initialized) or (max_w != self.last_w or max_h != self.last_h):
            self._initialize_raindrops(max_w, max_h)
        # Update raindrop positions every 100 frames for smoothness.
        if dt % 100 == 0:
            for drop in self.raindrops:
                if self.direction == "down":
                    drop["y"] += 1
                    if drop["y"] >= max_h - 1:
                        drop["y"] = 1
                        drop["x"] = random.randint(1, max_w - 2)
                elif self.direction == "left":
                    drop["x"] -= 1
                    if drop["x"] < 1:
                        drop["x"] = max_w - 2
                        drop["y"] = random.randint(1, max_h - 2)
                elif self.direction == "right":
                    drop["x"] += 1
                    if drop["x"] >= max_w - 1:
                        drop["x"] = 1
                        drop["y"] = random.randint(1, max_h - 2)
        attr = get_color_attr(self.color_name)
        for drop in self.raindrops:
            ch = '|' if self.direction == "down" else '-'
            draw_inside_frame_ch(stdscr, drop["y"], drop["x"], ch, attr)